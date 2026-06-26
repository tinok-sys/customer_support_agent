import os
from dotenv import load_dotenv

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.1

EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_STORE_PATH = "data/vector_store"

MAX_CONVERSATION_TURNS = 10
