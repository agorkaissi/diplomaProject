from pathlib import Path

from ollama_client import generate_answer

def load_documents(folder:str) ->list[tuple[str,str]]:
    path = Path(folder)
    path.mkdir(parents=True, exist_ok=True)

    documents: list[tuple[str,str]] = []
    for file in path.glob("*.txt"):
        content = file.read_text(encoding="utf-8", errors="ignore")
        documents.append((file.name, content))

    return documents

def retrieve_relevant_documents(
        question: str,
        documents: list[tuple[str,str]],
        top_k:int =2
) -> list[tuple[str,str]]:
    question_words = set(question.lower().split())
    scored_documents: list[tuple[int,str,str]] = []

    for file_name, content in documents:
        content = content.lower()
        score = sum(1 for word in question_words if word in content.lower())
        if score > 0:
            scored_documents.append((score, file_name, content))

    scored_documents.sort(key=lambda item: item[0], reverse=True)
    return [(name,content) for score, name, content in scored_documents[:top_k]]

def build_prompt(agent_prompt:str, question:str, context:str)->str:
    return f"""
    {agent_prompt}

    Answer only from the context below.
    If the context is insufficient, say: I don't know based on the provided documents.

    Context:
    {context}

    Question:
    {question}
    """.strip()

def run_agent(question:str, agent) -> tuple[str, list[str]]:
    documents = load_documents(agent.docs_path)
    relevant_documents = retrieve_relevant_documents(question, documents)

    if not relevant_documents:
        return "I don't know based on the provided documents", []

    context = "\n\n---\n\n".join(
        f"[source: {file_name}]\n{content}"
        for file_name , content in relevant_documents
    )

    prompt = build_prompt(
        agent_prompt=agent.prompt,
        question =question,
        context=context
    )

    answer = generate_answer(prompt)
    sources = [file_name for file_name, _ in relevant_documents]
    return answer, sources
