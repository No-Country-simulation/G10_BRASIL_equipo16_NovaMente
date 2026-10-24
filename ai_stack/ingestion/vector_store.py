import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from ai_stack.config import CHROMA_DB_PATH

def create_vector_db(chunks: list[Document], embedding_model: HuggingFaceEmbeddings) -> Chroma:
    if not chunks:
        raise ValueError("Chunks não pode estar vazio")
        
    if not embedding_model:
        raise ValueError("Modelo de embedding não pode estar vazio")
    
    # Se DB já existe com dados, só adiciona
    if os.path.exists(CHROMA_DB_PATH) and os.path.isdir(CHROMA_DB_PATH) and os.listdir(CHROMA_DB_PATH):
        db_vector = Chroma(
            embedding_function=embedding_model,
            persist_directory=CHROMA_DB_PATH)
        db_vector.add_documents(chunks)
        return db_vector
        
    db_vector = Chroma.from_documents( 
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )
    return db_vector