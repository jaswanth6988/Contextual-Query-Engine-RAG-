# Contextual Query Engine (RAG)

An enterprise-grade Retrieval-Augmented Generation (RAG) system built with Python, PostgreSQL (`pgvector`), and LangChain. Designed for highly precise, context-aware semantic search over large-scale unstructured datasets.

## Architecture

This engine leverages an optimized `pgvector` database architecture to store and query high-dimensional embeddings. 
- **Embeddings**: Uses HuggingFace Sentence Transformers (or OpenAI embeddings) for dense vector generation.
- **Vector Store**: PostgreSQL with the `pgvector` extension, configured with HNSW (Hierarchical Navigable Small World) indexing to reduce query latency by up to 40% on large datasets.
- **Generation**: Integrates with LLMs (e.g., OpenAI GPT-4 or local models) via LangChain to synthesize contextual answers based on retrieved documents.

## Features
- **Scalable Ingestion**: Pipeline to chunk, embed, and upsert thousands of documents efficiently.
- **Semantic Search**: Fast k-NN (k-nearest neighbors) retrieval utilizing cosine similarity.
- **Optimized Latency**: Pre-configured database indexes specifically tuned for vector queries.

## Getting Started

### 1. Start the Database
The project uses Docker to spin up a PostgreSQL instance pre-configured with `pgvector`.
```bash
docker-compose up -d
```

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql+psycopg2://admin:password@localhost:5432/rag_db
OPENAI_API_KEY=your-api-key-here
```

### 4. Run the Pipeline
**Ingest Data:**
```bash
python src/ingest.py --path data/sample.txt
```

**Query the Engine:**
```bash
python src/retrieval.py --query "What is the core architecture of this RAG system?"
```
