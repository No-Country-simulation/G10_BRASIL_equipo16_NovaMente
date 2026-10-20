from langchain_huggingface import HuggingFaceEmbeddings
from typing import Optional

def get_embeddings_model(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> HuggingFaceEmbeddings:
    if not model_name or model_name.strip() == "":
        raise ValueError("Nome do modelo não pode ser vazio")

    try:
        model = HuggingFaceEmbeddings(model_name=model_name)
        return model
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar modelo de embeddings '{model_name}': {e}") from e