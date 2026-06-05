from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from db import get_db
from models import Agent, AgentLink
from schemas import AgentCreate, AgentResponse, AgentUpdateSafe
from services.agent_service import (
    create_supervisor_links,
    to_agent_response,
)


router = APIRouter(
    prefix="/agents",
    tags=["agents"],
)


@router.get("", response_model=list[AgentResponse])
def list_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).order_by(Agent.id.asc()).all()
    return [to_agent_response(agent) for agent in agents]


@router.post("", response_model=AgentResponse)
def create_agent(payload: AgentCreate, db: Session = Depends(get_db)):
    existing_agent = db.query(Agent).filter(Agent.name == payload.name).first()

    if existing_agent:
        raise HTTPException(
            status_code=400,
            detail="Agent already exists",
        )

    if payload.agent_type == "specialist" and payload.connected_agent_ids:
        raise HTTPException(
            status_code=400,
            detail="Only supervisor agents can have connected agents",
        )

    if payload.agent_type == "supervisor" and not payload.connected_agent_ids:
        raise HTTPException(
            status_code=400,
            detail="Supervisor agent must have at least one connected agent",
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


@router.patch("/{agent_id}/deactivate")
def deactivate_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    agent.active = False

    db.query(AgentLink).filter(
        or_(
            AgentLink.supervisor_agent_id == agent.id,
            AgentLink.child_agent_id == agent.id,
        )
    ).update({"active": False}, synchronize_session=False)

    db.commit()

    return {
        "message": f"Agent '{agent.name}' was deactivated successfully",
    }


@router.patch("/{agent_id}/activate")
def activate_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    agent.active = True

    db.query(AgentLink).filter(
        or_(
            AgentLink.supervisor_agent_id == agent.id,
            AgentLink.child_agent_id == agent.id,
        )
    ).update({"active": True}, synchronize_session=False)

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return {
        "message": f"Agent '{agent.name}' was activated successfully",
    }


@router.patch("/{agent_id}")
def update_agent(agent_id: int, data: AgentUpdateSafe, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
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
            "prompt": agent.prompt,
        },
    }