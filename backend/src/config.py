"""Read backend-only settings. Never return API keys to the browser."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    provider: str = field(
        default_factory=lambda: os.getenv("MODEL_PROVIDER", "auto").strip().lower()
    )
    openai_api_key: str = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY", "").strip(), repr=False
    )
    openai_chat_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    )
    openai_embedding_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    )
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    chat_model: str = os.getenv("CHAT_MODEL", "qwen2.5:3b")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    data_dir: str = os.getenv("DATA_DIR", "./data/chroma")
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    max_pdf_mb: int = int(os.getenv("MAX_PDF_MB", "20"))
    rerank_model: str = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

    @property
    def active_provider(self) -> str:
        if self.provider == "auto":
            return "openai" if self.openai_api_key else "ollama"
        return self.provider

    @property
    def active_chat_model(self) -> str:
        return self.openai_chat_model if self.active_provider == "openai" else self.chat_model

    @property
    def active_embedding_model(self) -> str:
        return (
            self.openai_embedding_model
            if self.active_provider == "openai"
            else self.embedding_model
        )

    def __post_init__(self):
        if self.provider not in {"auto", "openai", "ollama"}:
            raise ValueError("MODEL_PROVIDER must be auto, openai or ollama.")
        if self.provider == "openai" and not self.openai_api_key:
            raise ValueError("Set OPENAI_API_KEY or use MODEL_PROVIDER=auto for Ollama.")
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError("Require 0 <= CHUNK_OVERLAP < CHUNK_SIZE.")
        if self.max_pdf_mb < 1:
            raise ValueError("MAX_PDF_MB must be positive.")
