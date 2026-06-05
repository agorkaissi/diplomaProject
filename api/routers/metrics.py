from fastapi import APIRouter

from services.metrics_service import get_rag_metrics_summary


router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
)


@router.get("/rag")
def get_rag_metrics():
    return get_rag_metrics_summary()