# Relationship to the source repository

Source: https://github.com/jaswanth6988/Contextual-Query-Engine-RAG-
Reviewed commit: fe2655d342020f5f549c86e5360a7b162d678580

The original contained a text-file loader, Hugging Face embeddings, a PostgreSQL/pgvector connection and a basic RetrievalQA script. Its ingestion CLI called `parser.add_argument()` in place of `parse_args()`. Imports used older LangChain module locations. The repository had no PDF upload app, page-source presentation, reranker or tool-calling workflow.

This ZIP is a focused replacement implementation matching the requested basic end-to-end PDF app. It keeps the project concept and Python/src organization, replaces PostgreSQL with local Chroma to remove database setup, uses LangChain integration packages, and adds a React/TypeScript UI and FastAPI API, citations, document management, tests and setup documentation. The old planning document and unimplemented claims are intentionally not included. No changes were pushed to GitHub.

To integrate, create a branch in your own checkout, copy these files in, and review and remove the superseded root `src/` scripts, requirements and old `PLAN.md`; the replacement code lives in `backend/` and `frontend/`. The new README describes the delivered implementation. Keep any existing license/history in your checkout.
