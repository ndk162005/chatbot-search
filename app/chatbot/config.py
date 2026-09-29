"""
Configuration settings for the PDF Chatbot module.
"""

from pathlib import Path

# Base directory for the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data directory
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database and vector storage paths
DATABASE_PATH = DATA_DIR / "chatbot.db"
VECTOR_DB_PATH = DATA_DIR / "chatbot_vectors"

# Default embedding model name
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# Ollama LLM settings
OLLAMA_MODEL = "qwen3:0.6b"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TIMEOUT = 180.0


