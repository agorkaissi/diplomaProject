from dataclasses import dataclass, field
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
    score: float


@dataclass(frozen=True)
class AgentRetrievalResult:
    agent_name: str
    chunks: list[RetrievedChunk] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    confidence: float = 0.0

    @property
    def has_context(self) -> bool:
        return bool(self.chunks)


@dataclass(frozen=True)
class AgentRagAnswer:
    agent_name: str
    answer: str
    chunks: list[RetrievedChunk] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    confidence: float = 0.0

    @property
    def has_answer(self) -> bool:
        return bool(self.answer.strip())