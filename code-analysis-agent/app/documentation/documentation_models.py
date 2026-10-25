
from typing import Literal

from pydantic import BaseModel, Field


DocumentType = Literal[
    "README",
    "ARCHITECTURE",
    "API_REFERENCE",
    "CONFIGURATION",
]


class DocumentationSection(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source_files: list[str] = Field(default_factory=list)


class GeneratedDocument(BaseModel):
    document_type: DocumentType
    title: str = Field(min_length=1)
    summary: str
    sections: list[DocumentationSection] = Field(
        default_factory=list
    )
    limitations: list[str] = Field(default_factory=list)


class DocumentationResult(BaseModel):
    repository: str
    generated_documents: list[GeneratedDocument] = Field(
        default_factory=list
    )
    warnings: list[str] = Field(default_factory=list)
