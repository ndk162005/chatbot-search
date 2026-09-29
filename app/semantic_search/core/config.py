from pathlib import Path


# ==================================================
# PROJECT PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

UPLOAD_DIR = BASE_DIR / "uploads"

DATABASE_DIR = DATA_DIR / "database"

VECTOR_DB_DIR = DATA_DIR / "vector_db"


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)


# ==================================================
# DATABASE
# ==================================================

DATABASE_PATH = DATABASE_DIR / "semantic_search.db"


# ==================================================
# VECTOR DATABASE
# ==================================================

VECTOR_DB_PATH = VECTOR_DB_DIR

CHROMA_COLLECTION_NAME = "pdf_paragraphs"


# ==================================================
# EMBEDDING
# ==================================================

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


# ==================================================
# SEARCH
# ==================================================

DEFAULT_TOP_K = 5

MAX_TOP_K = 20

MIN_RELEVANCE_SCORE = 0.0


# ==================================================
# PDF
# ==================================================

ALLOWED_FILE_EXTENSION = ".pdf"

MAX_FILE_SIZE_MB = 50