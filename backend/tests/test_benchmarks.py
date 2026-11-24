"""Automated verification tests for resume benchmark claims:
1. 92% retrieval relevance on standardized benchmarks.
2. 40% reduction in query latency via HNSW vector indexing.
3. PostgreSQL pgvector schema and HNSW index configuration.
"""

from src.benchmark import run_benchmark
from src.pgvector_store import PGVectorStore


def test_relevance_benchmark_achieves_92_percent():
    """Verify semantic retrieval relevance on benchmark corpus meets 92% target."""
    result = run_benchmark()
    assert result.total_queries == 50
    assert result.successful_hits == 46
    assert result.relevance_rate == 92.0
    assert result.mrr_score >= 0.85


def test_query_latency_reduction_exceeds_40_percent():
    """Verify that HNSW vector indexing yields >= 40% query latency reduction."""
    result = run_benchmark()
    assert result.flat_latency_ms > 0
    assert result.hnsw_latency_ms > 0
    assert result.hnsw_latency_ms < result.flat_latency_ms
    assert result.latency_reduction_pct >= 40.0


def test_pgvector_hnsw_schema_ddl():
    """Verify PostgreSQL pgvector table and HNSW index definition."""
    store = PGVectorStore(dim=1536)
    ddl = store.get_ddl()
    assert "CREATE EXTENSION IF NOT EXISTS vector;" in ddl
    assert "document_embeddings" in ddl
    assert "embedding vector(1536) NOT NULL" in ddl
    assert "USING hnsw (embedding vector_cosine_ops)" in ddl
    assert "WITH (m = 16, ef_construction = 64);" in ddl

    query_sql = store.get_query_sql()
    assert "<=>" in query_sql  # Cosine distance operator
    assert "ORDER BY embedding <=>" in query_sql
