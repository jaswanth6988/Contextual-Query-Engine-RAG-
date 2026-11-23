# Validation record

Validated on 23 November 2026 using Python 3.12 and Node.js 24.

| Check | Result |
|---|---|
| Backend `python -m pytest -q` | 12 tests passed |
| Backend Ruff lint | Passed |
| React `npm test` | 3 tests passed |
| React `npm run build` | Passed TypeScript checking and Vite production build |
| Fresh backend environment installation | Passed |
| Live Ollama embeddings and generation | Not tested; Ollama models were not installed in the build environment |
| Actual cross-encoder weights / quality | Not tested; ordering is tested with a deterministic scoring stub |
| Docker compose | Provided, not executed |
| Browser screenshot / responsive visual inspection | Attempted but blocked by the environment's Chromium process restrictions |

## What the tests cover

Backend tests use real PDF bytes, pypdf extraction, LangChain chunking and a real persisted Chroma index. They check duplicate detection, page provenance, search ordering with controlled vectors, document filtering, reopened persistence, deletion, invalid/scanned files, reranking order, rollback after a partial failed insert, configuration isolation, grounded prompt construction and tool dispatch.

FastAPI integration tests exercise multipart upload, document listing, all three query modes, delete and invalid requests through HTTP TestClient. Model outputs are stubbed; these checks do not demonstrate real model quality or model-driven tool selection.

React tests exercise submitting a question, rendering source pages, file upload feedback, confirmed removal, backend error display and retry availability. They use mocked API responses and a simulated DOM, not a live browser/model end-to-end session.

The model-facing application code uses actual OpenAI and Ollama integrations. OpenAI selection, factory arguments and separate provider indexes are tested without network requests; no live OpenAI call was made because no API key was supplied. Test doubles are confined to the test suite; no fake embedding or fake answer mode is exposed in the application.

## Manual model checklist on your laptop

1. Download both models and start Ollama, FastAPI and React using the README.
2. Upload the sample PDF; verify one or more chunks from both pages.
3. Ask about annual leave; inspect the cited page and the 24-day answer.
4. Ask about the learning budget; inspect page 2 and INR 15,000.
5. Ask an unrelated question and assess whether the model declines to invent an answer.
6. Try agent mode; inspect actual selected tools and arguments.
7. Enable optional reranking and compare source ordering.
8. Restart the backend and check persistence, duplicates and deletion.
9. Test your own PDFs and inspect extraction quality, especially tables and multi-column layouts.
10. Resize the browser to a phone width and verify controls and source cards.

Before claiming accuracy, create a labeled question/source dataset and measure retrieval hit rate, answer correctness and citation validity. No performance or accuracy benchmark is claimed in this delivery.
