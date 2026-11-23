"""Request/response shapes. FastAPI validates them and generates /docs."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    mode: Literal["ask", "search", "agent"] = "ask"
    document_id: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    rerank: bool = False

    @field_validator("question")
    @classmethod
    def reject_blank_question(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Enter a question.")
        return value.strip()


class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunks: int


class UploadResponse(BaseModel):
    status: str
    chunks: int
    skipped_pages: list[int]


class Source(BaseModel):
    label: str
    chunk_id: str
    filename: str
    page: int
    text: str
    cosine_distance: float
    rerank_score: float | None


class ToolStep(BaseModel):
    tool: str
    arguments: dict
    fallback: bool = False


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]
    trace: list[ToolStep]
