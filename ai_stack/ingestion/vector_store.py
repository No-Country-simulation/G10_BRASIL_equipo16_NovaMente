import os
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from ai_stack.config import CHROMA_DB_PATH

def validar_chunks_ids(chunks: list[Document]):
    if not chunks:
        raise ValueError("Chunks não pode estar vazio")
        
    if not all(isinstance(chunk, Document) for chunk in chunks):
        raise ValueError("Todos os elementos de chunks devem ser instâncias de Document")
    
    
    chunks_ids= [chunk.metadata.get("chunk_id") for chunk in chunks]

    if not chunks_ids: 
        raise ValueError("Nenhum chunk com chunk_id válido")
    
    if not all(isinstance(chunk_id,str)for chunk_id in  chunks_ids):
        raise ValueError("chunk_id deve ser uma string")
    
    if any(chunk_id.strip() == "" for chunk_id in chunks_ids):
        raise ValueError("chunk_id não pode ser vazio ou apenas espaços em branco")
    
   
    if len(chunks_ids) != len(set(chunks_ids)):
        raise ValueError("Existem chunks com chunk_id duplicados")
    
    return set(chunks_ids)


def create_vector_db(chunks: list[Document], embedding_model: HuggingFaceEmbeddings) -> Chroma:
    if embedding_model is None:
        raise ValueError("embedding_model não pode estar vazio")
    chunks_ids= validar_chunks_ids(chunks)
    db_vector= Chroma( embedding_function=embedding_model, persist_directory=CHROMA_DB_PATH)
    # Obtém o dicionário de dados da BD; se 'ids' não existir, devolve uma lista vazia por defeito
    dados_atuais = db_vector.get()
    ids_existentes = set(dados_atuais.get("ids", [])) if dados_atuais else set()

    chunks_ids_novos = chunks_ids-ids_existentes
    novo_chunks= [chunk for chunk in chunks if chunk.metadata.get("chunk_id")in chunks_ids_novos]
    if novo_chunks:
        db_vector.add_documents(novo_chunks, ids=[chunk.metadata.get("chunk_id") for chunk in novo_chunks])
        
    return db_vector