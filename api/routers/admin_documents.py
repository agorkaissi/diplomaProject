import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from db import get_db
from models import Agent
from retrieval.ingest_service import ingest_agent
from services.document_service import validate_file_extension


router = APIRouter(
    prefix="/admin/documents",
    tags=["admin-documents"],
)


@router.post("/upload/{agent_name}")
async def upload_document_for_agent(
    agent_name: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    agent = (
        db.query(Agent)
        .filter(Agent.name == agent_name)
        .filter(Agent.active.is_(True))
        .first()
    )

    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent not found: {agent_name}",
        )

    if agent.agent_type != "specialist":
        raise HTTPException(
            status_code=400,
            detail="Documents can only be uploaded to specialist agents",
        )

    if not agent.docs_path:
        raise HTTPException(
            status_code=400,
            detail=f"Agent '{agent.name}' has no docs_path configured",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Missing filename",
        )

    validate_file_extension(file.filename)

    docs_dir = Path(agent.docs_path).resolve()
    docs_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = Path(file.filename).name
    target_path = docs_dir / safe_filename

    with target_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingest_result = ingest_agent(agent)

    return {
        "status": "ok",
        "message": "Document uploaded and agent index rebuilt successfully.",
        "agent": agent.name,
        "filename": safe_filename,
        "saved_to": str(target_path),
        "ingest": ingest_result,
    }