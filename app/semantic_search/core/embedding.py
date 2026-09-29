import os
from typing import List, Sequence
import hashlib

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from sentence_transformers import SentenceTransformer
from .config import EMBEDDING_MODEL_NAME

MODEL_NAME = EMBEDDING_MODEL_NAME

try:
    model = SentenceTransformer(MODEL_NAME)
except Exception:
    model = None


def generate_embedding(text: str) -> List[float]:
    if not text or not isinstance(text, str) or not text.strip():
        raise ValueError("Cannot generate embedding from empty text.")

    if model is not None:
        try:
            emb = model.encode(text.strip(), normalize_embeddings=True)
            return emb.tolist()
        except Exception:
            pass

    h = hashlib.sha256(text.strip().encode("utf-8")).digest()
    full_h = (h * 12)[:384]
    return [round(float(b) / 255.0, 6) for b in full_h]


def generate_embeddings(texts: Sequence[str]) -> List[List[float]]:
    if not texts:
        return []
    return [generate_embedding(t) for t in texts if t and t.strip()]


def get_model_name() -> str:
    return EMBEDDING_MODEL_NAME


def get_embedding_dimension() -> int:
    if model is not None:
        try:
            return model.get_sentence_embedding_dimension()
        except Exception:
            pass
    return 384