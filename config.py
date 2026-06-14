import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

LLM_MODEL = "llama-3.3-70b-versatile"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

CHUNKS_FILE = "chunks.jsonl"
CHROMA_PATH = "./chroma_db"
CHROMA_COLLECTION = "unofficial_guide"

N_RESULTS = 5
