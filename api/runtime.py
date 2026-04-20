from sqlalchemy.orm import Session

from models import Agent, AgentLink
from ollama_client import generate_answer
from prompts.builders import build_specialist_prompt, build_supervisor_prompt
from retrieval.loader import load_documents


def retrieve_relevant_documents(
    question: str,
    documents: list[tuple[str, str]],
    top_k: int = 2,
) -> list[tuple[str, str]]:
    question_words = set(question.lower().split())
    scored_documents: list[tuple[int, str, str]] = []

    for file_name, content in documents:
        content_lower = content.lower()
        score = sum(1 for word in question_words if word in content_lower)
        if score > 0:
            scored_documents.append((score, file_name, content))

    if not scored_documents:
        scored_documents = [(0, name, content) for name, content in documents[:top_k]]

    scored_documents.sort(key=lambda item: item[0], reverse=True)
    return [
        (file_name, content)
        for score, file_name, content in scored_documents[:top_k]
    ]


def is_unknown_answer(answer: str) -> bool:
    normalized = answer.strip().lower()
    return (
        "i don't know based on the provided documents" in normalized
        or "i don't know based on the provided agent answers" in normalized
    )


def run_specialist_agent(question: str, agent) -> tuple[str, list[str]]:
    documents = load_documents(agent.docs_path)
    relevant_documents = retrieve_relevant_documents(question, documents)

    if not relevant_documents:
        return "I don't know based on the provided documents", []

    context = "\n\n---\n\n".join(
        f"[{file_name}]\n{content[:800]}"
        for file_name, content in relevant_documents
    )

    prompt = build_specialist_prompt(
        agent_prompt=agent.prompt,
        question=question,
        context=context,
    )

    answer = generate_answer(prompt)
    sources = [file_name for file_name, _ in relevant_documents]
    return answer, sources


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

    if len(links) == 1:
        child = (
            db.query(Agent)
            .filter(
                Agent.id == links[0].child_agent_id,
                Agent.active.is_(True),
            )
            .first()
        )

        if not child:
            return "Child agent not found", []

        context, sources = run_specialist_retrieval_only(question, child)

        if not context.strip() and not sources:
            return "I don't know based on the provided agent answers.", []

        prompt = build_supervisor_prompt(
            agent_prompt=agent.prompt,
            question=question,
            child_answers=f"[{child.name}]\n{context}",
        )

        final_answer = generate_answer(prompt)
        return final_answer, sources

    child_agents = (
        db.query(Agent)
        .filter(
            Agent.id.in_([l.child_agent_id for l in links]),
            Agent.active.is_(True),
        )
        .all()
    )

    child_map = {a.id: a for a in child_agents}

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

        useful_child_answers.append(f"[{child.name}]\n{context}")
        collected_sources.extend([f"{child.name}:{s}" for s in sources])

    if not useful_child_answers:
        return "I don't know based on the provided agent answers.", []

    prompt = build_supervisor_prompt(
        agent_prompt=agent.prompt,
        question=question,
        child_answers="\n\n---\n\n".join(useful_child_answers),
    )

    final_answer = generate_answer(prompt)

    return final_answer, collected_sources


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

    return run_specialist_agent(question=question, agent=agent)


def run_agent(question: str, agent: Agent, db: Session) -> tuple[str, list[str]]:
    return _run_agent(
        question=question,
        agent=agent,
        db=db,
    )


def run_specialist_retrieval_only(question: str, agent) -> tuple[str, list[str]]:
    documents = load_documents(agent.docs_path)
    relevant_documents = retrieve_relevant_documents(question, documents)

    if not relevant_documents:
        return "", []

    context = "\n\n---\n\n".join(
        f"[source: {file_name}]\n{content}"
        for file_name, content in relevant_documents
    )

    sources = [file_name for file_name, _ in relevant_documents]

    return context, sources