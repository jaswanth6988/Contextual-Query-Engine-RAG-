import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://admin:password@localhost:5432/rag_db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
