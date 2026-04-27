from sqlalchemy.orm import Session

from models import Agent, AgentLink
from ollama_client import generate_answer
from prompts.builders import build_specialist_prompt, build_supervisor_prompt
from retrieval.retriever import retrieve_chunks_for_folder
from retrieval.types import AgentRagAnswer, AgentRetrievalResult, RetrievedChunk


SPECIALIST_TOP_K = 3


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


def _calculate_confidence(chunks: list[RetrievedChunk]) -> float:
    if not chunks:
        return 0.0

    best_score = max(item.score for item in chunks)
    average_score = sum(item.score for item in chunks) / len(chunks)

    return round((best_score * 0.7) + (average_score * 0.3), 4)


def _format_retrieved_chunks(chunks: list[RetrievedChunk]) -> str:
    return "\n\n---\n\n".join(
        (
            f"[source: {item.chunk.source_file} | "
            f"chunk: {item.chunk.chunk_id} | "
            f"chars: {item.chunk.start_char}-{item.chunk.end_char} | "
            f"score: {item.score:.4f}]\n"
            f"{item.chunk.content}"
        )
        for item in chunks
    )


def _format_agent_result_for_supervisor(result: AgentRagAnswer) -> str:
    chunk_context = _format_retrieved_chunks(result.chunks)

    sources = ", ".join(result.sources) if result.sources else "none"

    return f"""
[agent: {result.agent_name}]
[confidence: {result.confidence:.4f}]
[sources: {sources}]

Answer:
{result.answer}

Retrieved evidence:
{chunk_context}
""".strip()


def run_specialist_retrieval_only(
    question: str,
    agent: Agent,
    top_k: int = SPECIALIST_TOP_K,
) -> AgentRetrievalResult:
    relevant_chunks = retrieve_chunks_for_folder(
        question=question,
        folder=agent.docs_path,
        top_k=top_k,
        agent_name=agent.name,
    )

    sources = _unique_sources_from_chunks(
        [item.chunk.source_file for item in relevant_chunks]
    )

    confidence = _calculate_confidence(relevant_chunks)

    return AgentRetrievalResult(
        agent_name=agent.name,
        chunks=relevant_chunks,
        sources=sources,
        confidence=confidence,
    )


def run_specialist_rag_answer(
    question: str,
    agent: Agent,
    top_k: int = SPECIALIST_TOP_K,
) -> AgentRagAnswer:
    retrieval_result = run_specialist_retrieval_only(
        question=question,
        agent=agent,
        top_k=top_k,
    )

    if not retrieval_result.has_context:
        return AgentRagAnswer(
            agent_name=agent.name,
            answer="I don't know based on the provided documents",
            chunks=[],
            sources=[],
            confidence=0.0,
        )

    context = _format_retrieved_chunks(retrieval_result.chunks)

    prompt = build_specialist_prompt(
        agent_prompt=agent.prompt,
        question=question,
        context=context,
    )

    answer = generate_answer(prompt)

    return AgentRagAnswer(
        agent_name=agent.name,
        answer=answer,
        chunks=retrieval_result.chunks,
        sources=retrieval_result.sources,
        confidence=retrieval_result.confidence,
    )


def run_specialist_agent(question: str, agent: Agent) -> tuple[str, list[str]]:
    result = run_specialist_rag_answer(
        question=question,
        agent=agent,
    )

    return result.answer, result.sources


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

    useful_child_results: list[AgentRagAnswer] = []
    collected_sources: list[str] = []

    for link in links:
        child = child_map.get(link.child_agent_id)

        if not child:
            continue

        child_result = run_specialist_rag_answer(
            question=question,
            agent=child,
        )

        if child_result.has_answer and not is_unknown_answer(child_result.answer):
            useful_child_results.append(child_result)
            collected_sources.extend(
                [f"{child_result.agent_name}:{source}" for source in child_result.sources]
            )

    if not useful_child_results:
        return "I don't know based on the provided agent answers.", []

    useful_child_results.sort(
        key=lambda item: item.confidence,
        reverse=True,
    )

    child_answers = "\n\n---\n\n".join(
        _format_agent_result_for_supervisor(result)
        for result in useful_child_results
    )

    prompt = build_supervisor_prompt(
        agent_prompt=agent.prompt,
        question=question,
        child_answers=child_answers,
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