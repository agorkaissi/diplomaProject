from retrieval.chunking import chunk_documents
from retrieval.embeddings import cosine_similarity, embed_text, embed_texts
from retrieval.loader import load_documents
from retrieval.types import DocumentChunk, RetrievedChunk, SourceDocument

DEFAULT_TOP_K = 3
MIN_SIMILARITY_SCORE = 0.25


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
    min_score: float = MIN_SIMILARITY_SCORE,
) -> list[RetrievedChunk]:
    if not chunks:
        return []

    chunk_texts = [chunk.content for chunk in chunks]

    question_embedding = embed_text(question)
    chunk_embeddings = embed_texts(chunk_texts)

    similarity_scores = cosine_similarity(
        query_embedding=question_embedding,
        document_embeddings=chunk_embeddings,
    )

    scored_chunks = [
        RetrievedChunk(
            chunk=chunk,
            score=float(score),
        )
        for chunk, score in zip(chunks, similarity_scores)
        if float(score) >= min_score
    ]

    scored_chunks.sort(
        key=lambda item: item.score,
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
    min_score: float = MIN_SIMILARITY_SCORE,
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
        min_score=min_score,
    )