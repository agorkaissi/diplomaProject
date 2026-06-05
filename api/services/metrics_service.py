from collections import deque


rag_metrics_store = deque(maxlen=1000)


def add_rag_metrics(debug) -> None:
    rag_metrics_store.append(
        {
            "retrieval_time_ms": debug.retrieval_time_ms,
            "reranking_time_ms": debug.reranking_time_ms,
            "generation_time_ms": debug.generation_time_ms,
            "total_time_ms": debug.total_time_ms,
            "confidence": debug.confidence,
            "agent_type": debug.agent_type,
            "language_model": debug.language_model,
            "use_reranker": debug.use_reranker,
            "chunks": len(debug.chunks),
        }
    )


def get_rag_metrics_summary() -> dict:
    if not rag_metrics_store:
        return {
            "avg_retrieval_time_ms": 0,
            "avg_reranking_time_ms": 0,
            "avg_generation_time_ms": 0,
            "avg_total_time_ms": 0,
            "avg_confidence": 0,
            "requests": 0,
            "reranker_requests": 0,
        }

    n = len(rag_metrics_store)

    return {
        "avg_retrieval_time_ms": sum(
            item["retrieval_time_ms"] for item in rag_metrics_store
        ) / n,
        "avg_reranking_time_ms": sum(
            item["reranking_time_ms"] for item in rag_metrics_store
        ) / n,
        "avg_generation_time_ms": sum(
            item["generation_time_ms"] for item in rag_metrics_store
        ) / n,
        "avg_total_time_ms": sum(
            item["total_time_ms"] for item in rag_metrics_store
        ) / n,
        "avg_confidence": sum(
            item["confidence"] for item in rag_metrics_store
        ) / n,
        "requests": n,
        "reranker_requests": sum(
            1 for item in rag_metrics_store if item["use_reranker"]
        ),
    }