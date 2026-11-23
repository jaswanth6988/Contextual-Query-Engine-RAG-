from io import BytesIO

import pytest
from langchain_core.embeddings import Embeddings
from langchain_core.messages import AIMessage
from reportlab.pdfgen import canvas

from src.agent import ask_agent
from src.config import Settings
from src.engine import Engine
from src.ingest import parse_pdf


class TestEmbeddings(Embeddings):
    """Tiny deterministic test vectors; never used by the application."""

    __test__ = False

    def embed_documents(self, texts):
        return [self.embed_query(t) for t in texts]

    def embed_query(self, text):
        text = text.lower()
        return [float(text.count(w)) for w in ["orbit", "planet", "bread", "flour"]] + [0.1]


class FakeLLM:
    def __init__(self):
        self.messages = []
        self.steps = 0

    def bind_tools(self, tools):
        self.tools = tools
        return self

    def invoke(self, messages):
        self.messages = messages
        if hasattr(self, "tools") and self.steps == 0:
            self.steps += 1
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "search_documents",
                        "args": {"query": "planet orbit"},
                        "id": "call_1",
                        "type": "tool_call",
                    }
                ],
            )
        return AIMessage(content="The planet follows an orbit. [S1]")


def pdf(*pages):
    stream = BytesIO()
    writer = canvas.Canvas(stream)
    for text in pages:
        writer.drawString(50, 750, text)
        writer.showPage()
    writer.save()
    return stream.getvalue()


@pytest.fixture
def engine(tmp_path):
    return Engine(Settings(data_dir=str(tmp_path)), TestEmbeddings(), FakeLLM())


def test_ingest_search_persist_filter_delete(engine):
    first = pdf("The planet follows an orbit.", "Bread requires flour.")
    assert engine.ingest(first, "science.pdf")["chunks"] == 2
    assert engine.ingest(first, "renamed.pdf")["status"] == "already indexed"
    hit = engine.search("planet orbit", k=1)[0]
    assert hit["page"] == 1 and "planet" in hit["text"]
    engine.ingest(pdf("Bread flour recipe"), "recipe.pdf")
    doc_id = next(d["id"] for d in engine.documents() if d["filename"] == "recipe.pdf")
    assert all(s["filename"] == "recipe.pdf" for s in engine.search("planet", doc_id=doc_id))
    reopened = Engine(engine.settings, TestEmbeddings(), FakeLLM())
    assert len(reopened.documents()) == 2
    reopened.delete(doc_id)
    assert len(reopened.documents()) == 1


def test_invalid_empty_scanned(engine):
    for bad in [b"", b"not a pdf", b"%PDF-corrupt"]:
        with pytest.raises(ValueError):
            engine.ingest(bad, "bad.pdf")
    with pytest.raises(ValueError, match="OCR"):
        engine.ingest(pdf(""), "scan.pdf")
    with pytest.raises(ValueError):
        engine.search(" ")
    assert engine.answer("What is here?")["sources"] == []


def test_page_metadata_and_skipped(engine):
    _, chunks, skipped = parse_pdf(pdf("", "Text on second page"), "../safe.pdf", engine.settings)
    assert skipped == [1]
    assert chunks[0].metadata["page"] == 2
    assert chunks[0].metadata["filename"] == "safe.pdf"


def test_answer_and_agent_grounding(engine):
    engine.ingest(pdf("The planet follows an orbit."), "science.pdf")
    result = engine.answer("What follows an orbit?")
    assert result["sources"][0]["label"] == "S1"
    assert "PDF excerpts" in engine.llm.messages[-1].content
    result = ask_agent(engine, "Explain the planet orbit")
    assert result["trace"][0]["tool"] == "search_documents"
    assert result["sources"][0]["page"] == 1


def test_reranking(engine, monkeypatch):
    engine.ingest(pdf("The planet follows an orbit.", "Bread requires flour."), "mixed.pdf")

    class Ranker:
        def predict(self, pairs):
            return [10 if "Bread" in text else -10 for _, text in pairs]

    monkeypatch.setattr("src.engine.load_reranker", lambda _: Ranker())
    assert engine.search("planet", rerank=True, k=1)[0]["page"] == 2


def test_rollback(engine, monkeypatch):
    original = engine.store.add_documents

    def fail_after_write(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("simulated embedding failure")

    monkeypatch.setattr(engine.store, "add_documents", fail_after_write)
    with pytest.raises(RuntimeError):
        engine.ingest(pdf("Planet orbit"), "failed.pdf")
    assert engine.documents() == []


def test_configuration_isolates_indexes(engine):
    engine.ingest(pdf("Planet orbit"), "science.pdf")
    different = Engine(
        Settings(data_dir=engine.settings.data_dir, chunk_size=500), TestEmbeddings(), FakeLLM()
    )
    assert different.documents() == []
