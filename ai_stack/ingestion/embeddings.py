from langchain_huggingface import HuggingFaceEmbeddings
from ai_stack.config import EMBEDDING_MODEL

_model_instance = None
    
def get_embeddings_model( ) -> HuggingFaceEmbeddings:
    global _model_instance
    if _model_instance is not None:
        return _model_instance 
    try:
        _model_instance = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, 
        model_kwargs ={"device":"cpu"},
        encode_kwargs={ "normalize_embeddings": True})
        return _model_instance
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar modelo '{EMBEDDING_MODEL}': {e}") from e
        