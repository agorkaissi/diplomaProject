from sqlalchemy.orm import Session

from models import Agent, AgentLink
from ollama_client import generate_answer
from prompts.builders import build_specialist_prompt, build_supervisor_prompt
from retrieval.retriever import retrieve_chunks_for_folder


def is_unknown_answer(answer: str) -> bool:
    normalized = answer.strip().lower()
    return (
        "i don't know based on the provided documents" in normalized
        or "i don't know based on the provided agent answers" in normalized
    )


def _unique_sources_from_chunks(sources: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_sources: list[str] = []

    for source in sources:
        if source not in seen:
            seen.add(source)
            unique_sources.append(source)

    return unique_sources


def run_specialist_agent(question: str, agent: Agent) -> tuple[str, list[str]]:
    relevant_chunks = retrieve_chunks_for_folder(
        question=question,
        folder=agent.docs_path,
        top_k=3,
        agent_name=agent.name,
    )

    if not relevant_chunks:
        return "I don't know based on the provided documents", []

    context = "\n\n---\n\n".join(
        (
            f"[source: {item.chunk.source_file} | "
            f"chunk: {item.chunk.chunk_id} | "
            f"chars: {item.chunk.start_char}-{item.chunk.end_char} | "
            f"score: {item.score:.4f}]\n"
            f"{item.chunk.content}"
        )
        for item in relevant_chunks
    )

    prompt = build_specialist_prompt(
        agent_prompt=agent.prompt,
        question=question,
        context=context,
    )

    answer = generate_answer(prompt)
    sources = _unique_sources_from_chunks(
        [item.chunk.source_file for item in relevant_chunks]
    )
    return answer, sources


def run_specialist_retrieval_only(question: str, agent: Agent) -> tuple[str, list[str]]:
    relevant_chunks = retrieve_chunks_for_folder(
        question=question,
        folder=agent.docs_path,
        top_k=3,
        agent_name=agent.name,
    )

    if not relevant_chunks:
        return "", []

    context = "\n\n---\n\n".join(
        (
            f"[source: {item.chunk.source_file} | "
            f"chunk: {item.chunk.chunk_id} | "
            f"chars: {item.chunk.start_char}-{item.chunk.end_char} | "
            f"score: {item.score:.4f}]\n"
            f"{item.chunk.content}"
        )
        for item in relevant_chunks
    )

    sources = _unique_sources_from_chunks(
        [item.chunk.source_file for item in relevant_chunks]
    )

    return context, sources


def run_supervisor_agent(
    question: str,
    agent: Agent,
    db: Session,
) -> tuple[str, list[str]]:
    links = (
        db.query(AgentLink)
        .filter(
            AgentLink.supervisor_agent_id == agent.id,
            AgentLink.active.is_(True),
        )
        .order_by(AgentLink.sort_order.asc(), AgentLink.id.asc())
        .all()
    )

    if not links:
        return "No connected agents are configured for this supervisor", []

    child_agents = (
        db.query(Agent)
        .filter(
            Agent.id.in_([link.child_agent_id for link in links]),
            Agent.active.is_(True),
        )
        .all()
    )

    child_map = {child.id: child for child in child_agents}

    useful_child_answers: list[str] = []
    collected_sources: list[str] = []

    for link in links:
        child = child_map.get(link.child_agent_id)
        if not child:
            continue

        context, sources = run_specialist_retrieval_only(
            question=question,
            agent=child,
        )

        if context.strip():
            useful_child_answers.append(f"[{child.name}]\n{context}")
            collected_sources.extend([f"{child.name}:{source}" for source in sources])

    if not useful_child_answers:
        return "I don't know based on the provided agent answers.", []

    prompt = build_supervisor_prompt(
        agent_prompt=agent.prompt,
        question=question,
        child_answers="\n\n---\n\n".join(useful_child_answers),
    )

    final_answer = generate_answer(prompt)
    unique_sources = _unique_sources_from_chunks(collected_sources)

    return final_answer, unique_sources


def _run_agent(
    question: str,
    agent: Agent,
    db: Session,
) -> tuple[str, list[str]]:
    if agent.agent_type == "supervisor":
        return run_supervisor_agent(
            question=question,
            agent=agent,
            db=db,
        )

    return run_specialist_agent(
        question=question,
        agent=agent,
    )


def run_agent(
    question: str,
    agent: Agent,
    db: Session,
) -> tuple[str, list[str]]:
    return _run_agent(
        question=question,
        agent=agent,
        db=db,
    )