from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List

def chunker(docs: List[Document]) -> List[Document]:
    if not docs:
        raise ValueError('Lista de Documentos vazia ou nula')
    
    docsFiltrados = [
        doc for doc in docs
        if doc.page_content and doc.page_content.strip() != ""
    ]
    
    if not docsFiltrados:
        raise ValueError('Nenhum documento com conteudo valido após filtro')
            
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    if splitter._chunk_size <= splitter._chunk_overlap:
        raise ValueError('chunk_size deve ser maior que chunk_overlap')
        
    chunks = splitter.split_documents(docsFiltrados)
    return chunks