from typing import TypeAlias

DocumentName: TypeAlias = str
DocumentContent: TypeAlias = str
LoadedDocument: TypeAlias = tuple[DocumentName, DocumentContent]
LoadedDocuments: TypeAlias = list[LoadedDocument]