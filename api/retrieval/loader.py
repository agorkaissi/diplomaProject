from pathlib import Path

from retrieval.types import LoadedDocuments

DOCUMENT_CACHE: dict[str, LoadedDocuments] = {}


def load_documents(folder: str) -> LoadedDocuments:
    if folder in DOCUMENT_CACHE:
        return DOCUMENT_CACHE[folder]

    path = Path(folder)
    path.mkdir(parents=True, exist_ok=True)

    documents: LoadedDocuments = []
    for file in path.glob("*.txt"):
        content = file.read_text(encoding="utf-8", errors="ignore")
        documents.append((file.name, content))

    DOCUMENT_CACHE[folder] = documents
    return documents