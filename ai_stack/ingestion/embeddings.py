
from langchain_huggingface import HuggingFaceEmbeddings
from ai_stack.config import EMBEDDING_MODEL


_instancia_modelo = None


def obter_modelo_embeddings() -> HuggingFaceEmbeddings:
    global _instancia_modelo

    if _instancia_modelo is not None:
        return _instancia_modelo

    try:
        _instancia_modelo = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

        return _instancia_modelo

    except Exception as erro:
        raise RuntimeError(
            f"Erro ao carregar modelo '{EMBEDDING_MODEL}': {erro}"
        ) from erro
