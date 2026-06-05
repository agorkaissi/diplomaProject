import re
from pathlib import Path

from fastapi import HTTPException


DATA_DIR = Path("data").resolve()
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


def validate_folder_name(folder_name: str) -> None:
    if not re.match(r"^[a-zA-Z0-9_-]+$", folder_name):
        raise HTTPException(
            status_code=400,
            detail="Invalid folder name",
        )


def validate_file_extension(filename: str) -> None:
    ext = Path(filename).suffix.lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}",
        )


def resolve_safe_data_folder(folder_name: str) -> Path:
    validate_folder_name(folder_name)

    target_folder = (DATA_DIR / folder_name).resolve()

    if DATA_DIR not in target_folder.parents and target_folder != DATA_DIR:
        raise HTTPException(
            status_code=400,
            detail="Invalid folder path",
        )

    return target_folder


def resolve_safe_file_path(folder_name: str, filename: str) -> Path:
    target_folder = resolve_safe_data_folder(folder_name)
    file_path = (target_folder / filename).resolve()

    if target_folder not in file_path.parents:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )

    return file_path