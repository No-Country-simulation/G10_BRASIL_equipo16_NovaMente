from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
from ai_stack.config import CHUNK_SIZE, CHUNK_OVERLAP

def validar_docs(docs):
    if not docs:
        raise ValueError('Lista de Documentos vazia ou nula')

def validar_identidade_documentos(docs: List[Document]) -> None:
    versoes_por_documento = {}

    for indice, doc in enumerate(docs):

        # 1. Validar o tipo do documento
        if not isinstance(doc, Document):
            raise TypeError(
                f"O elemento na posição {indice} não é um Document"
            )

        # 2. Obter e validar os metadados
        metadata = doc.metadata

        if not isinstance(metadata, dict):
            raise TypeError(
                f"Os metadados do documento {indice} devem ser um dicionário"
            )

        for campo in ("document_id", "document_version"):

            # Verificar se o campo existe
            if campo not in metadata or metadata[campo] is None:
                raise ValueError(
                    f"Documento na posição {indice} sem {campo}"
                )

            valor = metadata[campo]

            # Verificar o tipo
            if not isinstance(valor, str):
                raise TypeError(
                    f"{campo} deve ser uma string"
                )

            # Verificar se está vazio
            if not valor.strip():
                raise ValueError(
                    f"{campo} não pode estar vazio"
                )

            # Evitar identificadores com espaços nas extremidades
            if valor != valor.strip():
                raise ValueError(
                    f"{campo} não deve conter espaços nas extremidades"
                )

        # 3. Obter os identificadores já validados
        document_id = metadata["document_id"]
        document_version = metadata["document_version"]

        # 4. Verificar consistência das versões
        if document_id in versoes_por_documento:

            if versoes_por_documento[document_id] != document_version:
                raise ValueError(
                    f"O documento {document_id} possui versões "
                    "diferentes na mesma ingestão"
                )

        else:
            versoes_por_documento[document_id] = document_version
def chunker(docs: List[Document]) -> List[Document]:
    validar_docs(docs)
    
    validar_identidade_documentos(docs)

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
            document_id = chunk.metadata["document_id"]
            document_version = chunk.metadata["document_version"]

            page = chunk.metadata.get("page")
            page_ref = f"p{page}" if page is not None else "sem-pagina"

            chunk.metadata["chunk_index"] = i

            chunk.metadata["chunk_id"] = (
                f"{document_id}_{document_version}_{page_ref}_c{i}")
        chunks.extend(chunk_atual)
    return chunks      
        
        