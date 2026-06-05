import os
from datetime import datetime
from mimetypes import guess_type

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from services.document_service import (
    DATA_DIR,
    resolve_safe_data_folder,
    resolve_safe_file_path,
)


router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)


@router.get("")
async def list_document_folders():
    if not DATA_DIR.exists():
        return {"folders": []}

    folders = []

    for path in DATA_DIR.iterdir():
        if path.is_dir():
            folders.append(
                {
                    "name": path.name,
                }
            )

    return {
        "folders": folders,
    }


@router.get("/{folder_name}")
async def get_documents(folder_name: str):
    target_folder = resolve_safe_data_folder(folder_name)

    if not target_folder.exists():
        raise HTTPException(
            status_code=404,
            detail="Folder not found",
        )

    documents = []

    for file_path in target_folder.iterdir():
        if not file_path.is_file():
            continue

        documents.append(
            {
                "filename": file_path.name,
                "extension": file_path.suffix.lower(),
                "size_bytes": file_path.stat().st_size,
                "modified_at": datetime.fromtimestamp(
                    os.path.getmtime(file_path)
                ).isoformat(),
            }
        )

    documents.sort(
        key=lambda item: item["modified_at"],
        reverse=True,
    )

    return {
        "folder": folder_name,
        "documents": documents,
    }


@router.get("/{folder_name}/{filename}")
async def get_document(
    folder_name: str,
    filename: str,
    download: bool = False,
):
    file_path = resolve_safe_file_path(folder_name, filename)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    mime_type, _ = guess_type(file_path)

    if download:
        return FileResponse(
            path=file_path,
            media_type="application/octet-stream",
            headers={"Content-Disposition": "attachment"},
        )

    return FileResponse(
        path=file_path,
        media_type=mime_type or "text/plain",
        headers={"Content-Disposition": "inline"},
    )


@router.delete("/{folder_name}/{filename}")
async def delete_document(
    folder_name: str,
    filename: str,
):
    file_path = resolve_safe_file_path(folder_name, filename)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    file_path.unlink()

    return {
        "message": "File deleted successfully",
        "folder": folder_name,
        "filename": filename,
    }