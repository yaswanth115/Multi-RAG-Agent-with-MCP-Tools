import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

LLM_MODEL = "openai/gpt-oss-120b"
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

TOP_K = 5
