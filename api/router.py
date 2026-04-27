import re
from typing import Optional, TypedDict

from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from models import Agent
from retrieval.retriever import retrieve_chunks_for_folder


ROUTER_TOP_K = 3
ROUTER_MIN_CONFIDENCE = 0.30
ROUTER_MULTI_AGENT_MARGIN = 0.06

AGENT_NAME_BOOST = 0.60
CONTENT_KEYWORD_BOOST_LIMIT = 0.25


class RouterState(TypedDict, total=False):
    question: str
    selected_agent: Optional[str]
    route: str


def _normalize_text(value: str) -> str:
    return value.strip().lower()


def _tokenize(value: str) -> set[str]:
    normalized = _normalize_text(value)
    normalized = re.sub(r"[^a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ0-9]+", " ", normalized)

    return {
        token
        for token in normalized.split()
        if len(token) >= 3
    }


def _calculate_route_confidence(scores: list[float]) -> float:
    if not scores:
        return 0.0

    best_score = max(scores)
    average_score = sum(scores) / len(scores)

    return round((best_score * 0.75) + (average_score * 0.25), 4)


def _calculate_agent_name_boost(question: str, agent: Agent) -> float:
    question_normalized = _normalize_text(question)
    agent_name_normalized = _normalize_text(agent.name)

    if agent_name_normalized and agent_name_normalized in question_normalized:
        return AGENT_NAME_BOOST

    question_tokens = _tokenize(question)
    agent_tokens = _tokenize(agent.name)

    if question_tokens & agent_tokens:
        return AGENT_NAME_BOOST

    return 0.0


def _calculate_content_keyword_boost(question: str, chunks) -> float:
    question_tokens = _tokenize(question)

    if not question_tokens:
        return 0.0

    matched_tokens: set[str] = set()

    for item in chunks:
        chunk_tokens = _tokenize(
            f"{item.chunk.source_file} {item.chunk.content}"
        )
        matched_tokens |= question_tokens & chunk_tokens

    if not matched_tokens:
        return 0.0

    ratio = len(matched_tokens) / len(question_tokens)
    return min(ratio * 0.20, CONTENT_KEYWORD_BOOST_LIMIT)


def _get_active_supervisor(db: Session) -> Optional[Agent]:
    return (
        db.query(Agent)
        .filter(
            Agent.agent_type == "supervisor",
            Agent.active.is_(True),
        )
        .order_by(Agent.id.asc())
        .first()
    )


def _get_active_specialists(db: Session) -> list[Agent]:
    return (
        db.query(Agent)
        .filter(
            Agent.agent_type == "specialist",
            Agent.active.is_(True),
        )
        .order_by(Agent.id.asc())
        .all()
    )


def _resolve_selected_agent(db: Session, selected_agent: Optional[str]) -> Optional[str]:
    if not selected_agent:
        return None

    selected_normalized = _normalize_text(selected_agent)

    agent = (
        db.query(Agent)
        .filter(
            Agent.active.is_(True),
        )
        .all()
    )

    for item in agent:
        if _normalize_text(item.name) == selected_normalized:
            return item.name

    return None


def _resolve_semantic_route(db: Session, question: str) -> str:
    supervisor = _get_active_supervisor(db)
    specialists = _get_active_specialists(db)

    if not specialists:
        if supervisor:
            return supervisor.name

        raise ValueError("No active agent found.")

    scored_candidates: list[tuple[Agent, float, float, float]] = []

    for specialist in specialists:
        chunks = retrieve_chunks_for_folder(
            question=question,
            folder=specialist.docs_path,
            top_k=ROUTER_TOP_K,
            agent_name=specialist.name,
            min_score=0.0,
        )

        semantic_scores = [item.score for item in chunks]
        semantic_confidence = _calculate_route_confidence(semantic_scores)

        name_boost = _calculate_agent_name_boost(
            question=question,
            agent=specialist,
        )

        content_boost = _calculate_content_keyword_boost(
            question=question,
            chunks=chunks,
        )

        final_score = semantic_confidence + name_boost + content_boost

        scored_candidates.append(
            (
                specialist,
                final_score,
                semantic_confidence,
                name_boost,
            )
        )

    scored_candidates.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    best_agent, best_score, best_semantic, best_name_boost = scored_candidates[0]

    if best_score < ROUTER_MIN_CONFIDENCE:
        if supervisor:
            return supervisor.name

        return best_agent.name

    if len(scored_candidates) >= 2 and supervisor:
        second_agent, second_score, _, _ = scored_candidates[1]
        score_gap = best_score - second_score

        if (
            best_name_boost == 0.0
            and second_score >= ROUTER_MIN_CONFIDENCE
            and score_gap <= ROUTER_MULTI_AGENT_MARGIN
        ):
            return supervisor.name

    return best_agent.name


def _resolve_route(
    db: Session,
    question: str,
    selected_agent: Optional[str],
) -> str:
    manually_selected = _resolve_selected_agent(
        db=db,
        selected_agent=selected_agent,
    )

    if manually_selected:
        return manually_selected

    return _resolve_semantic_route(
        db=db,
        question=question,
    )


def route_with_langgraph(
    db: Session,
    question: str,
    selected_agent: Optional[str] = None,
) -> str:
    def router_node(state: RouterState) -> RouterState:
        route = _resolve_route(
            db=db,
            question=state["question"],
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