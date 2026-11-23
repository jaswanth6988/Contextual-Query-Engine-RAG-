# A beginner's tour

## Start with one user action

When you click **Get answer**, React sends your question to FastAPI. FastAPI validates it, asks the RAG engine for an answer, and sends JSON back. React stores that JSON in state and renders it.

Read these files in this order:

1. `frontend/src/types.ts`: the data shapes shared with the API.
2. `frontend/src/api.ts`: small functions for GET, POST and DELETE requests. `fetch` is the browser's built-in HTTP client. FormData uploads files without manually setting a multipart boundary.
3. `frontend/src/App.tsx`: state and event handlers. `useState` stores what the screen needs; `useEffect` loads documents when the app starts. `async/await` waits for the server without blocking the browser.
4. `frontend/src/components/QuestionPanel.tsx`: a component gets values and callbacks through props. It displays inputs and calls the parent's callback on submit.
5. `backend/src/schemas.py`: Pydantic models validate incoming JSON and document outgoing fields. Bad data is rejected before the engine runs.
6. `backend/src/api.py`: each route has one job: validate, call an engine method and return data. `Depends` supplies a shared engine, and tests can replace it.
7. `backend/src/ingest.py`: extract PDF text page-by-page, then split it. Keeping page numbers before chunking makes citations possible.
8. `backend/src/engine.py`: stores chunks, retrieves evidence and generates answers.
9. `backend/src/models.py`: selects OpenAI when a key is configured, or Ollama otherwise.
10. `backend/src/agent.py`: the extra tool-calling workflow, after you understand standard RAG.

## Three modes, three purposes

- **Semantic search** returns relevant passages, without generating an answer. This helps debug retrieval.
- **Ask documents** always retrieves first, then sends evidence to the LLM.
- **Agent mode** lets the model request tools and reformulate searches. The app executes only known read-only tools and limits the number of steps. The model receives each tool result as a `ToolMessage`. A final separate pass answers from collected evidence.

## Important concepts

An **embedding** is a numeric representation of text. Semantically related text should produce nearby vectors. The query uses the same embedding model as the indexed chunks.

A **vector database** stores these vectors together with their original text and metadata. Chroma persists them on disk so restarting does not require another upload.

**Chunk overlap** repeats a small amount of text across neighboring chunks. A sentence near a boundary is less likely to lose all its surrounding context. The current splitter operates on characters, not tokens.

**Reranking** is a second scoring step after vector retrieval. It cannot recover a relevant passage that was never retrieved among the candidates.

**RAG** supplies retrieved information to a language model at question time. It does not train or fine-tune the model on your PDFs.

**Tool calling** means the model returns a structured request such as `search_documents(query="annual leave policy")`. Python runs the actual function. The model does not execute arbitrary code.

## Why the code is structured this way

- UI components handle display. `App.tsx` coordinates state and actions.
- `api.ts` is the only frontend file that knows HTTP request details.
- FastAPI routes do not contain chunking or similarity logic.
- One `Engine` owns model connections and the Chroma store.
- A content hash prevents duplicate uploads; stable chunk IDs identify evidence.
- A lock and rollback protect the small local index during writes.
- Tests substitute embeddings/LLM responses to run without model downloads.

## Safe exercises to learn the project

1. Change a heading or CSS spacing and observe Vite's live update.
2. Add a sample PDF and inspect the resulting page evidence.
3. Change chunk size in `.env`, restart and re-index; compare results.
4. Enable reranking and compare source ordering for the same question.
5. Inspect API requests in your browser's Network panel.
6. Read the API tests and add a meaningful test for a new feature.
7. Create 20 questions with expected source pages and measure retrieval hit rate before claiming better accuracy.

Keep generated answers separate from verified facts. A convincing answer can still be wrong if extraction or retrieval failed.
