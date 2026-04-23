from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model(model_name: str = DEFAULT_EMBEDDING_MODEL) -> SentenceTransformer:
    return SentenceTransformer(model_name)


def embed_texts(
    texts: list[str],
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> np.ndarray:
    if not texts:
        return np.empty((0, 0), dtype=np.float32)

    model = get_embedding_model(model_name)

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.astype(np.float32)


def embed_text(
    text: str,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> np.ndarray:
    embeddings = embed_texts([text], model_name=model_name)

    if embeddings.shape[0] == 0:
        return np.empty((0,), dtype=np.float32)

    return embeddings[0]


def cosine_similarity(
    query_embedding: np.ndarray,
    document_embeddings: np.ndarray,
) -> np.ndarray:
    if query_embedding.size == 0 or document_embeddings.size == 0:
        return np.array([], dtype=np.float32)

    # embeddings są już znormalizowane, więc iloczyn skalarny = cosine similarity
    scores = np.matmul(document_embeddings, query_embedding)

    return scores.astype(np.float32)