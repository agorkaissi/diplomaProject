from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from db import Base, engine, get_db
from router import route_with_langgraph
from runtime import run_agent
from models import Agent, AgentLink
from schemas import AgentCreate, AgentResponse, AgentUpdateSafe, ChatRequest, ChatResponse
import models
import logging


logging.basicConfig(
    level=logging.ERROR,
    format="%(levelname)s | %(name)s | %(message)s"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
app = FastAPI(
    title="Diploma project",
    lifespan=lifespan,
)

def to_agent_response(agent:Agent) -> AgentResponse:
    connected_agent_ids = [
        link.child_agent_id
        for link in getattr(agent, "supervisor_links", [])
        if link.active
    ]

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        docs_path=agent.docs_path,
        prompt=agent.prompt,
        agent_type=agent.agent_type,
        active=agent.active,
        connected_agent_ids=connected_agent_ids,
    )

def validate_connected_agents(
        db:Session,
        connected_agent_ids: list[int],
        supervisor_id:int,
) -> None:
    if not connected_agent_ids:
        return

    child_agents = db.query(Agent).filter(Agent.id.in_(connected_agent_ids)).all()

    if len(child_agents) != len(set(connected_agent_ids)):
        raise HTTPException(
            status_code=400,
            detail="One or more connected agents do not exist",
        )

    for child in child_agents:
        if child.id == supervisor_id:
            raise HTTPException(
                status_code=400,
                detail="Supervisor cannot be linked to itself"
            )

def create_supervisor_links(
        db: Session,
        supervisor_id: int,
        connected_agent_ids: list[int],
) -> None:
    if not connected_agent_ids:
        return

    validate_connected_agents(
        db=db,
        connected_agent_ids=connected_agent_ids,
        supervisor_id=supervisor_id,
    )

    links = [
        AgentLink(
            supervisor_agent_id=supervisor_id,
            child_agent_id=child_id,
            active=True,
            sort_order= index +1,
        )
        for index, child_id in enumerate(connected_agent_ids)
    ]
    db.add_all(links)
    db.commit()

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

@app.get("/agents", response_model=list[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).order_by(Agent.id.asc()).all()
    return [to_agent_response(agent) for agent in agents]

@app.post("/agents", response_model=AgentResponse)
def create_agent(payload: AgentCreate, db: Session = Depends(get_db)):
    existing_agent = db.query(Agent).filter(Agent.name == payload.name).first()
    if existing_agent:
        raise HTTPException(
            status_code=400,
            detail="Agent already exists"
        )
    if payload.agent_type == "specialist" and payload.connected_agent_ids:
        raise HTTPException(
            status_code=400,
            detail="Only supervisor agents can have connected agents"
        )

    if payload.agent_type == "supervisor" and not payload.connected_agent_ids:
        raise HTTPException(
            status_code=400,
            detail="Supervisor agent must have at least one connected agent"
        )

    agent = Agent(
        name=payload.name,
        description=payload.description,
        docs_path=payload.docs_path,
        prompt=payload.prompt,
        agent_type=payload.agent_type,
        active=payload.active,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    Path(agent.docs_path).mkdir(parents=True, exist_ok=True)

    if payload.agent_type == "supervisor":
        create_supervisor_links(
            db=db,
            supervisor_id=agent.id,
            connected_agent_ids=payload.connected_agent_ids,
        )

    agent = db.query(Agent).filter(Agent.id == agent.id).first()
    return to_agent_response(agent)

@app.patch("/agents/{agent_id}/deactivate")
def deactivate_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    agent.active = False

    db.query(AgentLink).filter(
        or_(
            AgentLink.supervisor_agent_id == agent.id,
            AgentLink.child_agent_id == agent.id
        )
    ).update({"active": False}, synchronize_session=False)

    db.commit()

    return {
        "message": f"Agent '{agent.name}' was deactivated successfully"
    }

@app.patch("/agents/{agent_id}/activate")
def activate_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    agent.active = True

    db.query(AgentLink).filter(
        or_(
            AgentLink.supervisor_agent_id == agent.id,
            AgentLink.child_agent_id == agent.id
        )
    ).update({"active": True}, synchronize_session=False)

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {"message": f"Agent '{agent.name}' was activated successfully"}

@app.patch("/agents/{agent_id}")
def update_agent(agent_id: int, data: AgentUpdateSafe, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    agent.name = data.name
    agent.description = data.description
    agent.prompt = data.prompt

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "message": f"Agent '{agent.name}' updated successfully",
        "agent": {
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "prompt": agent.prompt
        }
    }

@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    agent_name = route_with_langgraph(
        db=db,
        question=payload.question,
        selected_agent=payload.selected_agent,
    )

    agent = (
        db.query(Agent)
        .filter(Agent.name == agent_name, Agent.active.is_(True))
        .first()
    )
    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    answer, sources = run_agent(payload.question, agent, db)

    return ChatResponse(
        agent=agent.name,
        answer=answer,
        sources=sources,
    )

