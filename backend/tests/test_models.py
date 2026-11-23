from unittest.mock import patch

import pytest
from test_pipeline import FakeLLM, TestEmbeddings, pdf

from src.config import Settings
from src.engine import Engine
from src.models import create_chat_model, create_embeddings


def test_auto_selects_provider_without_exposing_key():
    assert Settings(provider="auto", openai_api_key="").active_provider == "ollama"
    settings = Settings(provider="auto", openai_api_key="test-secret")
    assert settings.active_provider == "openai"
    assert settings.active_embedding_model == "text-embedding-3-small"
    assert "test-secret" not in repr(settings)
    assert Settings(provider="ollama", openai_api_key="test-secret").active_provider == "ollama"
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        Settings(provider="openai", openai_api_key="")


def test_openai_factory_parameters():
    settings = Settings(provider="auto", openai_api_key="test-secret")
    with patch("src.models.ChatOpenAI") as chat, patch("src.models.OpenAIEmbeddings") as embeddings:
        create_chat_model(settings)
        create_embeddings(settings)
        assert chat.call_args.kwargs["model"] == "gpt-4o-mini"
        assert embeddings.call_args.kwargs["model"] == "text-embedding-3-small"
        assert chat.call_args.kwargs["api_key"] == "test-secret"


def test_provider_indexes_are_isolated(tmp_path):
    local = Engine(Settings(data_dir=str(tmp_path), provider="ollama"), TestEmbeddings(), FakeLLM())
    local.ingest(pdf("Planet orbit"), "local.pdf")
    cloud = Engine(
        Settings(data_dir=str(tmp_path), provider="openai", openai_api_key="test-secret"),
        TestEmbeddings(),
        FakeLLM(),
    )
    assert cloud.documents() == []
    assert len(local.documents()) == 1
