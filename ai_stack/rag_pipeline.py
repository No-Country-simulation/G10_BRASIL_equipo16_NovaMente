import os
from typing import Optional

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Cache global em memória para evitar recarregar o modelo a cada execução
_EMBEDDINGS_MODEL: Optional[HuggingFaceEmbeddings] = None


def obter_modelo_embeddings() -> HuggingFaceEmbeddings:
    """Carrega o modelo do HuggingFace apenas na primeira chamada e mantém em cache na RAM."""
    global _EMBEDDINGS_MODEL
    if _EMBEDDINGS_MODEL is None:
        print(
            "🧠 Carregando modelo de embeddings local (all-MiniLM-L6-v2) na memória..."
        )
        _EMBEDDINGS_MODEL = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _EMBEDDINGS_MODEL


def carregar_documento(caminho_arquivo: str):
    """Identifica o tipo de arquivo e carrega seu conteúdo."""
    extensao = os.path.splitext(caminho_arquivo)[1].lower()

    if extensao == ".pdf":
        loader = PyPDFLoader(caminho_arquivo)
    elif extensao in [".md", ".markdown"]:
        loader = UnstructuredMarkdownLoader(caminho_arquivo)
    elif extensao in [".txt"]:
        loader = TextLoader(caminho_arquivo, encoding="utf-8")
    else:
        raise ValueError(f"Formato de arquivo não suportado: {extensao}")

    return loader.load()


def criar_base_vetorial(caminho_arquivo: str, persist_directory: Optional[str] = None):
    """Faz a ingestão, chunking e vetorização (em memória por padrão ou em disco se informado)."""
    print(f"📄 Carregando o arquivo: {caminho_arquivo}...")
    documentos = carregar_documento(caminho_arquivo)

    print("✂️ Dividindo o documento em chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_documents(documentos)
    print(f"   -> Total de chunks gerados: {len(chunks)}")

    embeddings = obter_modelo_embeddings()

    print("⚡ Indexando vetores no ChromaDB...")
    if persist_directory:
        vectorstore = Chroma.from_documents(
            documents=chunks, embedding=embeddings, persist_directory=persist_directory
        )
    else:
        # Execução em memória RAM (mais rápida e sem criar arquivos temporários em disco)
        vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)

    print("✅ Base vetorial criada com sucesso!")
    return vectorstore


def buscar_contexto(vectorstore, query: str, k: int = 3):
    """Realiza uma busca semântica por trechos relevantes."""
    print(f"\n🔍 Buscando por: '{query}'")
    resultados = vectorstore.similarity_search(query, k=k)
    return resultados


# Exemplo de execução local para teste
if __name__ == "__main__":
    arquivo_exemplo = "exemplo_documento.pdf"

    if os.path.exists(arquivo_exemplo):
        db = criar_base_vetorial(arquivo_exemplo)

        pergunta_teste = "Qual é o objetivo principal desta documentação?"
        docs_relevantes = buscar_contexto(db, pergunta_teste)

        print("\n--- Trechos Encontrados ---")
        for i, doc in enumerate(docs_relevantes):
            print(
                f"\n[Chunk {i + 1}] (Fonte: {doc.metadata.get('source', 'Desconhecida')})"
            )
            print(doc.page_content[:300] + "...")
    else:
        print(
            f"⚠️ Coloque um arquivo chamado '{arquivo_exemplo}' na pasta para testar o script."
        )
