from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models import Agent
from router import route_with_langgraph
from runtime import run_agent_with_debug
from schemas import (
    ChatRequest,
    ChatResponse,
    ChatDebugResponse,
    RetrievedChunkResponse,
)
from services.metrics_service import add_rag_metrics


router = APIRouter(
    tags=["chat"],
)


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    agent_name = route_with_langgraph(
        db=db,
        question=payload.question,
        selected_agent=payload.selected_agent,
    )

    agent = (
        db.query(Agent)
        .filter(Agent.name == agent_name, Agent.active.is_(True))
        .first()
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    answer, sources, debug = run_agent_with_debug(
        question=payload.question,
        agent=agent,
        db=db,
        language_model=payload.language_model,
        use_reranker=payload.use_reranker,
    )

    add_rag_metrics(debug)

    return ChatResponse(
        agent=agent.name,
        answer=answer,
        sources=sources,
        debug=ChatDebugResponse(
            agent_type=debug.agent_type,
            language_model=debug.language_model,
            use_reranker=debug.use_reranker,
            retrieval_time_ms=debug.retrieval_time_ms,
            reranking_time_ms=debug.reranking_time_ms,
            generation_time_ms=debug.generation_time_ms,
            total_time_ms=debug.total_time_ms,
            confidence=debug.confidence,
            chunks=[
                RetrievedChunkResponse(
                    agent=item.chunk.agent_name,
                    source_file=item.chunk.source_file,
                    chunk_id=item.chunk.chunk_id,
                    score=round(item.score, 4),
                    start_char=item.chunk.start_char,
                    end_char=item.chunk.end_char,
                    content=item.chunk.content,
                )
                for item in debug.chunks
            ],
        ),
    )