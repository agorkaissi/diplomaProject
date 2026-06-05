from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import get_db
from retrieval.ingest_service import (
    ingest_all_agents,
    ingest_agent_by_name,
)


router = APIRouter(
    prefix="/admin/ingest",
    tags=["admin-ingest"],
)


@router.post("/all")
def admin_ingest_all(db: Session = Depends(get_db)):
    return ingest_all_agents(db)


@router.post("/agent/{agent_name}")
def admin_ingest_agent(agent_name: str, db: Session = Depends(get_db)):
    return ingest_agent_by_name(db, agent_name)