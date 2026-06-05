from fastapi import APIRouter

from ollama_client import list_llm_models


router = APIRouter()


@router.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}


@router.get("/llm-models")
def get_llm_models():
    return list_llm_models()