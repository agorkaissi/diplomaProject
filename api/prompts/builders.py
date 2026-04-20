def build_specialist_prompt(agent_prompt: str, question: str, context: str) -> str:
    return f"""
    {agent_prompt}

    Answer only from the context below.
    If the context is insufficient, say: I don't know based on the provided documents.

    Context:
    {context}

    Question:
    {question}
    """.strip()


def build_supervisor_prompt(agent_prompt: str, question: str, child_answers: str) -> str:
    return f"""
    {agent_prompt}

    You are supervisor agent.
    Answer the user question using only the child agent answers below.
    If one child answer already contains the answer, use it.
    If multiple child answers contain useful information, combine them.
    Do not invent information.
    Only say "I don't know based on the provided agent answers." if none of the child answers contain the answer.

    Child agent answers:
    {child_answers}

    User question:
    {question}
    """.strip()