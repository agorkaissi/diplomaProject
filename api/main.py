from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import Base, engine, get_db
from router import route_with_langgraph
from runtime import run_agent
from models import Agent
from schemas import AgentCreate, AgentResponse, ChatRequest, ChatResponse
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

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

@app.get("/agents", response_model=list[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    return db.query(Agent).order_by(Agent.id.asc()).all()

@app.post("/agents", response_model=AgentResponse)
def create_agent(payload: AgentCreate, db: Session = Depends(get_db)):
    existing_agent = db.query(Agent).filter(Agent.name == payload.name).first()
    if existing_agent:
        raise HTTPException(status_code=400, detail="Agent already exists")

    agent = Agent(**payload.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)

    Path(agent.docs_path).mkdir(parents=True, exist_ok=True)

    return agent

@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.active = False
    db.commit()

    return {"message": f"Agent '{agent_id}' was deactivated successfully"}

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
        raise HTTPException(status_code=404, detail="Agent not found")

    answer, sources = run_agent(payload.question, agent)

    return ChatResponse(
        agent=agent.name,
        answer=answer,
        sources=sources,
    )

