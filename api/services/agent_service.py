from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Agent, AgentLink
from schemas import AgentResponse


def to_agent_response(agent: Agent) -> AgentResponse:
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
    db: Session,
    connected_agent_ids: list[int],
    supervisor_id: int,
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
                detail="Supervisor cannot be linked to itself",
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
            sort_order=index + 1,
        )
        for index, child_id in enumerate(connected_agent_ids)
    ]

    db.add_all(links)
    db.commit()