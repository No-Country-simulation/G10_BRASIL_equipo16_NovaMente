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
    chunks = splitter.split_documents(docsFiltrados)
    return chunks