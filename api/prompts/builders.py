def build_specialist_prompt(agent_prompt: str, question: str, context: str) -> str:
    return f"""
{agent_prompt}

You are a strict RAG specialist.

Use only the context below.
Do not repeat the user question as the answer.
Do not guess.
Do not invent facts.
If the context does not directly answer the question, say exactly:
I don't know based on the provided documents.

Answer in the same language as the user question.

Context:
{context}

User question:
{question}

Final answer:
""".strip()


def build_supervisor_prompt(agent_prompt: str, question: str, child_answers: str) -> str:
    return f"""
{agent_prompt}

You are a supervisor agent in a Multi-RAG system.

Use only the child agent answers and their retrieved evidence below.
Each child agent section may contain:
- agent name
- confidence score
- answer
- sources
- retrieved chunks

Rules:
1. Prefer answers with higher confidence and stronger retrieved evidence.
2. If multiple agents provide useful information, combine them.
3. Preserve source awareness in your reasoning.
4. Do not invent information.
5. If none of the child agent answers contain the answer, say:
I don't know based on the provided agent answers.

Child agent results:
{child_answers}

User question:
{question}
""".strip()