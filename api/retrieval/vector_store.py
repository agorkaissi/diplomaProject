import json
import re
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from api.retrieval.embeddings import DEFAULT_EMBEDDING_MODEL, embed_text, embed_texts
from api.retrieval.types import DocumentChunk, RetrievedChunk

INDEX_FILE_NAME = "faiss.index"
METADATA_FILE_NAME = "metadata.json"
DEFAULT_INDEXES_ROOT = Path(__file__).resolve().parents[1] / "indexes"
DEFAULT_MIN_SCORE = 0.25


def normalize_agent_index_name(agent_name: str | None, docs_path: str) -> str:
    raw_name = agent_name or Path(docs_path).name
    normalized = raw_name.strip().lower()
    normalized = re.sub(r"[^a-z0-9_-]+", "_", normalized)
    normalized = normalized.strip("_")
    return normalized or "unknown_agent"


def get_agent_index_dir(
    docs_path: str,
    agent_name: str | None = None,
    indexes_root: Path = DEFAULT_INDEXES_ROOT,
) -> Path:
    agent_index_name = normalize_agent_index_name(
        agent_name=agent_name,
        docs_path=docs_path,
    )
    return indexes_root / agent_index_name


def chunk_to_metadata(chunk: DocumentChunk) -> dict[str, Any]:
    return {
        "chunk_id": chunk.chunk_id,
        "document_id": chunk.document_id,
        "source_file": chunk.source_file,
        "docs_path": chunk.docs_path,
        "content": chunk.content,
        "start_char": chunk.start_char,
        "end_char": chunk.end_char,
        "agent_name": chunk.agent_name,
    }


def metadata_to_chunk(metadata: dict[str, Any]) -> DocumentChunk:
    return DocumentChunk(
        chunk_id=metadata["chunk_id"],
        document_id=metadata["document_id"],
        source_file=metadata["source_file"],
        docs_path=metadata["docs_path"],
        content=metadata["content"],
        start_char=int(metadata["start_char"]),
        end_char=int(metadata["end_char"]),
        agent_name=metadata.get("agent_name"),
    )


def index_exists(index_dir: Path) -> bool:
    return (
        (index_dir / INDEX_FILE_NAME).exists()
        and (index_dir / METADATA_FILE_NAME).exists()
    )


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    if embeddings.ndim != 2 or embeddings.shape[0] == 0:
        raise ValueError("Cannot build FAISS index from empty embeddings")

    dimension = embeddings.shape[1]

    # Embeddingi z SentenceTransformer są już normalizowane,
    # więc IndexFlatIP działa jak cosine similarity.
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype(np.float32))

    return index


def save_vector_index(
    chunks: list[DocumentChunk],
    index_dir: Path,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> None:
    if not chunks:
        raise ValueError("Cannot save vector index without chunks")

    index_dir.mkdir(parents=True, exist_ok=True)

    chunk_texts = [chunk.content for chunk in chunks]
    embeddings = embed_texts(
        texts=chunk_texts,
        model_name=model_name,
    )

    index = build_faiss_index(embeddings)

    faiss.write_index(
        index,
        str(index_dir / INDEX_FILE_NAME),
    )

    metadata = {
        "embedding_model": model_name,
        "vector_count": len(chunks),
        "chunks": [chunk_to_metadata(chunk) for chunk in chunks],
    }

    (index_dir / METADATA_FILE_NAME).write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_vector_index(index_dir: Path) -> tuple[faiss.Index, list[DocumentChunk]]:
    index_path = index_dir / INDEX_FILE_NAME
    metadata_path = index_dir / METADATA_FILE_NAME

    if not index_path.exists():
        raise FileNotFoundError(f"Missing FAISS index file: {index_path}")

    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing metadata file: {metadata_path}")

    index = faiss.read_index(str(index_path))

    metadata = json.loads(
        metadata_path.read_text(encoding="utf-8"),
    )

    chunks = [
        metadata_to_chunk(chunk_metadata)
        for chunk_metadata in metadata.get("chunks", [])
    ]

    return index, chunks


def search_vector_index(
    question: str,
    index_dir: Path,
    top_k: int,
    min_score: float = DEFAULT_MIN_SCORE,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> list[RetrievedChunk]:
    if top_k <= 0:
        return []

    index, chunks = load_vector_index(index_dir=index_dir)

    if not chunks:
        return []

    question_embedding = embed_text(
        text=question,
        model_name=model_name,
    )

    if question_embedding.size == 0:
        return []

    query_vector = question_embedding.reshape(1, -1).astype(np.float32)

    scores, indexes = index.search(query_vector, top_k)

    results: list[RetrievedChunk] = []

    for score, chunk_index in zip(scores[0], indexes[0]):
        if chunk_index < 0:
            continue

        score_value = float(score)

        if score_value < min_score:
            continue

        if chunk_index >= len(chunks):
            continue

        results.append(
            RetrievedChunk(
                chunk=chunks[chunk_index],
                score=score_value,
            )
        )

    return results