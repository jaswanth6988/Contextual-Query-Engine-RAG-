"""One small factory for each model type; both use the same selected provider."""

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from src.config import Settings


def create_embeddings(settings: Settings):
    if settings.active_provider == "openai":
        return OpenAIEmbeddings(
            model=settings.active_embedding_model,
            api_key=settings.openai_api_key,
            request_timeout=120,
            max_retries=2,
        )
    return OllamaEmbeddings(model=settings.embedding_model, base_url=settings.base_url)


def create_chat_model(settings: Settings):
    if settings.active_provider == "openai":
        return ChatOpenAI(
            model=settings.active_chat_model,
            api_key=settings.openai_api_key,
            temperature=0,
            timeout=120,
            max_retries=2,
        )
    return ChatOllama(
        model=settings.chat_model,
        base_url=settings.base_url,
        temperature=0,
        num_ctx=8192,
        client_kwargs={"timeout": 120},
    )
