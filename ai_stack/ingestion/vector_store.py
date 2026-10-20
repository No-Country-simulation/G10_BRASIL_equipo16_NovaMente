import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings





DB_PATH="./chroma_novaMente.db"
def createDbVector(chunks : list[Document],embedding_model : HuggingFaceEmbeddings)->Chroma:
    
    if not chunks:
        raise ValueError("Chunks não pode estar vazio" )
        
    if not embedding_model:
        raise ValueError("Modelo de embedding não pode estar vazio" )
    
    
    if os.path.exists(DB_PATH) and os.listdir(DB_PATH):
        dbVector = Chroma(
            embedding_function=embedding_model,
            persist_directory=DB_PATH )
        dbVector.add_documents(chunks)
        return dbVector
        
    dbVector = Chroma.from_documents( 
    documents=chunks,
    embedding=embedding_model,
    persist_directory=DB_PATH
    )
    return dbVector
    
    