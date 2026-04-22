from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SourceDocument:
    document_id: str
    source_file: str
    content: str
    docs_path: str
    agent_name: Optional[str] = None


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    document_id: str
    source_file: str
    docs_path: str
    content: str
    start_char: int
    end_char: int
    agent_name: Optional[str] = None


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: DocumentChunk
    score: int