from langchain.vectorstores.pgvector import PGVector
from src.config import DATABASE_URL

def get_vector_store(embeddings, collection_name="document_embeddings"):
    """
    Initializes and returns the PGVector store.
    Utilizes pgvector for efficient similarity search.
    """
    store = PGVector(
        collection_name=collection_name,
        connection_string=DATABASE_URL,
        embedding_function=embeddings,
    )
    return store
