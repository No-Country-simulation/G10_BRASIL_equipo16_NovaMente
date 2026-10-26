from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
from ai_stack.config import CHUNK_SIZE, CHUNK_OVERLAP

def validar_docs(docs):
    if not docs:
        raise ValueError('Lista de Documentos vazia ou nula')

def chunker(docs: List[Document]) -> List[Document]:
    validar_docs(docs)
    
    docsFiltrados = [
        doc for doc in docs
        if doc.page_content and doc.page_content.strip() != ""
    ]
    
    if not docsFiltrados:
        raise ValueError('Nenhum documento com conteudo valido após filtro')
            
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = []
    for doc in docsFiltrados:
        chunk_atual= splitter.split_documents([doc])
        
        
        for i, chunk in enumerate(chunk_atual):
                source = chunk.metadata.get("source")
                page = chunk.metadata.get("page")
                if page is None:
                    page = 0
                    chunk.metadata["page"] = page
                chunk.metadata["chunk_index"]= i
                chunk.metadata["chunk_id"] = f'{source}_p{page}_c{i}' 
        chunks.extend(chunk_atual)
    return chunks      
        
        