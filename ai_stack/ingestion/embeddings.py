from langchain_huggingface import HuggingFaceEmbeddings
from ai_stack.config import EMBEDDING_MODEL

def get_embeddings_model(model_name: str = EMBEDDING_MODEL) -> HuggingFaceEmbeddings:
    if not model_name or not model_name.strip():
        raise ValueError("Nome do modelo não pode ser vazio")

    try:
        model = HuggingFaceEmbeddings(model_name=model_name)
        return model
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar modelo '{model_name}': {e}") from e
        