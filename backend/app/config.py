import os
from pathlib import Path
from dotenv import load_dotenv


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
INDEX_DIR = DATA_DIR / "index"

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(
    PROJECT_ROOT / ".env"
)


# ============================================================
# GROQ
# ============================================================

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY",
    ""
)

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)


# ============================================================
# RAG SETTINGS
# ============================================================

RELEVANCE_THRESHOLD = float(
    os.getenv(
        "RELEVANCE_THRESHOLD",
        "0.42"
    )
)

TOP_K = int(
    os.getenv(
        "TOP_K",
        "10"
    )
)