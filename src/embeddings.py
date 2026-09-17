from langchain.embeddings import HuggingFaceEmbeddings

def get_embedding_model(model_name="all-MiniLM-L6-v2"):
    """
    Loads a lightweight, highly efficient embedding model.
    """
    return HuggingFaceEmbeddings(model_name=model_name)
