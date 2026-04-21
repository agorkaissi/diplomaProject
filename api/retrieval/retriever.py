from retrieval.loader import load_documents
from retrieval.types import LoadedDocuments, ScoredDocuments


DEFAULT_TOP_K = 2


def retrieve_relevant_documents(
    question: str,
    documents: LoadedDocuments,
    top_k: int = DEFAULT_TOP_K,
) -> LoadedDocuments:
    question_words = set(question.lower().split())
    scored_documents: ScoredDocuments = []

    for file_name, content in documents:
        content_lower = content.lower()
        score = sum(1 for word in question_words if word in content_lower)

        if score > 0:
            scored_documents.append((score, file_name, content))

    if not scored_documents:
        scored_documents = [
            (0, file_name, content)
            for file_name, content in documents[:top_k]
        ]

    scored_documents.sort(key=lambda item: item[0], reverse=True)

    return [
        (file_name, content)
        for score, file_name, content in scored_documents[:top_k]
    ]


def retrieve_documents_for_folder(
    question: str,
    folder: str,
    top_k: int = DEFAULT_TOP_K,
) -> LoadedDocuments:
    documents = load_documents(folder)

    if not documents:
        return []

    return retrieve_relevant_documents(
        question=question,
        documents=documents,
        top_k=top_k,
    )