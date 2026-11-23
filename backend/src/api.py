"""HTTP layer only: validate requests, call the engine, return JSON.

The engine dependency is created once and can be replaced in tests.
Blocking model/PDF work runs in FastAPI's worker thread pool (plain def routes).
"""

import logging
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.agent import ask_agent
from src.engine import Engine
from src.schemas import DocumentInfo, QueryRequest, QueryResponse, UploadResponse

logger = logging.getLogger(__name__)
app = FastAPI(title="Contextual PDF RAG", version="1.0.0")


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return Engine()


@app.exception_handler(ValueError)
async def invalid_request(_request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def service_failure(_request, exc: Exception):
    logger.exception("RAG request failed", exc_info=exc)
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Request failed. Check the backend terminal, selected provider, API key or Ollama models."
        },
    )


@app.get("/api/health")
def health():
    # Liveness only: deliberately does not claim that models are downloaded.
    return {"status": "ok"}


@app.get("/api/config")
def config(engine: Engine = Depends(get_engine)):
    settings = engine.settings
    return {
        "provider": settings.active_provider,
        "chat_model": settings.active_chat_model,
        "embedding_model": settings.active_embedding_model,
        "max_pdf_mb": settings.max_pdf_mb,
    }


@app.get("/api/documents", response_model=list[DocumentInfo])
def list_documents(engine: Engine = Depends(get_engine)):
    with engine.lock:
        return engine.documents()


@app.post("/api/documents", response_model=UploadResponse)
def upload_document(file: UploadFile, engine: Engine = Depends(get_engine)):
    try:
        # Read at most the configured limit plus one byte to detect oversize files.
        data = file.file.read(engine.settings.max_pdf_mb * 1024 * 1024 + 1)
        return engine.ingest(data, file.filename or "document.pdf")
    finally:
        file.file.close()


@app.delete("/api/documents/{document_id}", status_code=204)
def delete_document(document_id: str, engine: Engine = Depends(get_engine)):
    with engine.lock:
        if document_id not in {d["id"] for d in engine.documents()}:
            raise HTTPException(status_code=404, detail="Document not found.")
        engine.delete(document_id)


@app.post("/api/query", response_model=QueryResponse)
def query_documents(body: QueryRequest, engine: Engine = Depends(get_engine)):
    # Serialize requests against writes for this local, single-user application.
    with engine.lock:
        if body.document_id and body.document_id not in {d["id"] for d in engine.documents()}:
            raise HTTPException(status_code=404, detail="Selected document no longer exists.")
        options = {"doc_id": body.document_id, "rerank": body.rerank}
        if body.mode == "search":
            sources = engine.search(body.question, **options)
            return {
                "answer": "Retrieved passages"
                if sources
                else "No indexed text found. Upload a PDF first.",
                "sources": sources,
                "trace": [],
            }
        if body.mode == "agent":
            return ask_agent(engine, body.question, **options)
        return engine.answer(body.question, **options)
