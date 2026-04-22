from pathlib import Path


def load_documents(folder: str) -> list[tuple[str, str]]:
    docs_path = Path(folder)

    if not docs_path.exists() or not docs_path.is_dir():
        return []

    documents: list[tuple[str, str]] = []

    for file_path in sorted(docs_path.glob("*.txt")):
        content = file_path.read_text(encoding="utf-8").strip()
        if content:
            documents.append((file_path.name, content))

    return documents