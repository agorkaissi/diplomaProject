from pathlib import Path

from retrieval.chunking import chunk_documents
from retrieval.loader import load_documents
from retrieval.types import RetrievedChunk, SourceDocument
from retrieval.vector_store import (
    DEFAULT_INDEXES_ROOT,
    get_agent_index_dir,
    index_exists,
    save_vector_index,
    search_vector_index,
)

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


def _build_and_save_index_for_folder(
    folder: str,
    agent_name: str | None,
    index_dir: Path,
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    source_documents = _build_source_documents(
        folder=folder,
        agent_name=agent_name,
    )

    if not source_documents:
        return

    chunks = chunk_documents(
        documents=source_documents,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    if not chunks:
        return

    save_vector_index(
        chunks=chunks,
        index_dir=index_dir,
    )


def retrieve_chunks_for_folder(
    question: str,
    folder: str,
    top_k: int = DEFAULT_TOP_K,
    agent_name: str | None = None,
    chunk_size: int = 700,
    chunk_overlap: int = 120,
    min_score: float = MIN_SIMILARITY_SCORE,
    force_rebuild: bool = False,
) -> list[RetrievedChunk]:
    index_dir = get_agent_index_dir(
        docs_path=folder,
        agent_name=agent_name,
        indexes_root=DEFAULT_INDEXES_ROOT,
    )

    if force_rebuild or not index_exists(index_dir):
        _build_and_save_index_for_folder(
            folder=folder,
            agent_name=agent_name,
            index_dir=index_dir,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    if not index_exists(index_dir):
        return []

    return search_vector_index(
        question=question,
        index_dir=index_dir,
        top_k=top_k,
        min_score=min_score,
    )