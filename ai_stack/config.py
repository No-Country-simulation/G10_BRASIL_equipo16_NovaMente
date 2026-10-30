from pathlib import Path

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL= "openai/gpt-oss-20b"
# FONTE versionada do time
RAG_SOURCE_PATH = Path("docs/rag/base-de-conhecimento")
# BANCO gerado local
CHROMA_DB_PATH = "./data/chroma_db"

if CHUNK_SIZE <= CHUNK_OVERLAP:
    raise ValueError("CHUNK_SIZE deve ser maior que CHUNK_OVERLAP")