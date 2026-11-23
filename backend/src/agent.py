"""A bounded, read-only tool-calling workflow using LangChain messages/tools."""

import json

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from src.engine import SYSTEM, context_text


def ask_agent(engine, question: str, doc_id: str | None = None, rerank: bool = False) -> dict:
    if not question.strip():
        raise ValueError("Enter a question.")
    evidence, trace = {}, []

    @tool
    def list_documents() -> str:
        """List indexed PDF filenames and their IDs."""
        return json.dumps([d for d in engine.documents() if not doc_id or d["id"] == doc_id])

    @tool
    def search_documents(query: str) -> str:
        """Search uploaded PDFs for evidence relevant to a focused query."""
        results = engine.search(query, doc_id=doc_id, rerank=rerank)
        for result in results:
            key = result["chunk_id"]
            if key not in evidence:
                evidence[key] = dict(result, label=f"S{len(evidence) + 1}")
        return (
            context_text([evidence[r["chunk_id"]] for r in results]) or "No matching indexed text."
        )

    available = {t.name: t for t in [list_documents, search_documents]}
    model = engine.llm.bind_tools(list(available.values()))
    messages = [
        SystemMessage(
            content=SYSTEM + "\nUse search_documents before answering. "
            "You may reformulate queries. Tools are read-only."
        ),
        HumanMessage(content=question),
    ]
    # Maximum three planning rounds and six calls. Final answer is a separate grounded pass.
    calls = 0
    for _ in range(3):
        reply = model.invoke(messages)
        if not reply.tool_calls:
            break
        messages.append(reply)
        for call in reply.tool_calls:
            calls += 1
            name = call["name"]
            if calls > 6:
                output = "Tool call budget reached."
            elif name not in available:
                output = "Unknown tool."
            else:
                output = available[name].invoke(call["args"])
            trace.append({"tool": name, "arguments": call["args"]})
            messages.append(ToolMessage(content=output, tool_call_id=call["id"]))
        if calls >= 6:
            break
    if not evidence:
        search_documents.invoke({"query": question})
        trace.append(
            {"tool": "search_documents", "arguments": {"query": question}, "fallback": True}
        )
    sources = list(evidence.values())
    if not sources:
        return {
            "answer": "No indexed text found. Upload a PDF first.",
            "sources": [],
            "trace": trace,
        }
    reply = engine.llm.invoke(
        [
            SystemMessage(content=SYSTEM),
            HumanMessage(content=f"Question: {question}\n\nPDF excerpts:\n{context_text(sources)}"),
        ]
    )
    return {"answer": reply.content, "sources": sources, "trace": trace}
