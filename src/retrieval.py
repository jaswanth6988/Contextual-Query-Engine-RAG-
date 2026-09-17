import argparse
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from src.embeddings import get_embedding_model
from src.db import get_vector_store
from src.config import OPENAI_API_KEY

def query_rag(question: str):
    embeddings = get_embedding_model()
    vector_store = get_vector_store(embeddings)

    # Initialize the LLM for generation
    llm = ChatOpenAI(
        temperature=0, 
        model_name="gpt-3.5-turbo",
        openai_api_key=OPENAI_API_KEY
    )

    # Build the RAG chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3})
    )

    print(f"\n[Query]: {question}")
    print("Searching vector space for contextual matches...")
    
    response = qa_chain.run(question)
    
    print(f"\n[Response]:\n{response}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the Contextual RAG engine.")
    parser.add_argument("--query", type=str, required=True, help="Your search query.")
    args = parser.parse_args()
    
    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY not found. Please set it in .env to use the generation module.")
    else:
        query_rag(args.query)
