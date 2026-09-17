import argparse
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.embeddings import get_embedding_model
from src.db import get_vector_store

def ingest_document(file_path: str):
    print(f"Loading document: {file_path}")
    loader = TextLoader(file_path)
    documents = loader.load()

    # Optimized chunking for context window
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )
    docs = text_splitter.split_documents(documents)
    print(f"Split into {len(docs)} chunks.")

    embeddings = get_embedding_model()
    vector_store = get_vector_store(embeddings)

    print("Generating embeddings and upserting into PostgreSQL (pgvector)...")
    vector_store.add_documents(docs)
    print("Ingestion complete. Indexes updated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into the RAG vector store.")
    parser.add_argument("--path", type=str, required=True, help="Path to the text document.")
    args = parser.add_argument()
    ingest_document(args.path)
