import re

from retrieval.chunking import chunk_documents
from retrieval.loader import load_documents
from retrieval.types import DocumentChunk, RetrievedChunk, SourceDocument

DEFAULT_TOP_K = 3

WORD_PATTERN = re.compile(r"\w+")


def _tokenize(text: str) -> set[str]:
    return {
        token.lower()
        for token in WORD_PATTERN.findall(text)
        if len(token) > 1
    }


def _build_source_documents(
    folder: str,
    agent_name: str | None = None,
) -> list[SourceDocument]:
    loaded_documents = load_documents(folder)

    source_documents: list[SourceDocument] = []
    for file_name, content in loaded_documents:
        source_documents.append(
            SourceDocument(
                document_id=f"{folder}:{file_name}",
                source_file=file_name,
                content=content,
                docs_path=folder,
                agent_name=agent_name,
            )
        )

    return source_documents


def retrieve_relevant_chunks(
    question: str,
    chunks: list[DocumentChunk],
    top_k: int = DEFAULT_TOP_K,
) -> list[RetrievedChunk]:
    question_words = _tokenize(question)

    if not chunks:
        return []

    scored_chunks: list[RetrievedChunk] = []

    for chunk in chunks:
        chunk_words = _tokenize(chunk.content)
        overlap_score = len(question_words.intersection(chunk_words))

        if overlap_score > 0:
            scored_chunks.append(
                RetrievedChunk(
                    chunk=chunk,
                    score=overlap_score,
                )
            )

    if not scored_chunks:
        fallback_chunks = chunks[:top_k]
        return [
            RetrievedChunk(chunk=chunk, score=0)
            for chunk in fallback_chunks
        ]

    scored_chunks.sort(
        key=lambda item: (
            item.score,
            -item.chunk.start_char,
        ),
        reverse=True,
    )

    return scored_chunks[:top_k]


def retrieve_chunks_for_folder(
    question: str,
    folder: str,
    top_k: int = DEFAULT_TOP_K,
    agent_name: str | None = None,
    chunk_size: int = 700,
    chunk_overlap: int = 120,
) -> list[RetrievedChunk]:
    source_documents = _build_source_documents(
        folder=folder,
        agent_name=agent_name,
    )

    if not source_documents:
        return []

    chunks = chunk_documents(
        documents=source_documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    if not chunks:
        return []

    return retrieve_relevant_chunks(
        question=question,
        chunks=chunks,
        top_k=top_k,
    )