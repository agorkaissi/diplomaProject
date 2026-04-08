from typing import Optional, TypedDict

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from models import Agent

class RouterState(TypedDict, total=False):
    question: str
    selected_agent: Optional[str]
    route: str

def _resolve_route(db: Session, selected_agent: Optional[str]) -> str:
    if selected_agent:
        agent = (
            db.query(Agent)
            .filter(Agent.name == selected_agent, Agent.active.is_(True))
            .first()
        )
        if agent:
            return agent.name

    fallback_agent = (
        db.query(Agent)
        .filter(Agent.active.is_(True))
        .order_by(Agent.id.asc())
        .first()
    )

    if not fallback_agent:
        raise ValueError("No active agent found.")

    return fallback_agent.name

def route_with_langgraph(
        db: Session,
        question: str,
        selected_agent: Optional[str] = None
) -> str:
    def router_node(state: RouterState)-> RouterState:
        route = _resolve_route(
            db=db,
            selected_agent=state.get("selected_agent"),
        )
        return {**state, "route": route}

    graph = StateGraph(RouterState)
    graph.add_node("router", router_node)
    graph.set_entry_point("router")
    graph.add_edge("router", END)

    app = graph.compile()
    result = app.invoke(
        {
            "question": question,
            "selected_agent": selected_agent,
        }
    )

    return result["route"]
