from ai_stack.ingestion.loader import reader
from ai_stack.ingestion.chunking import chunker
from ai_stack.ingestion.vector_store import create_vector_db
from ai_stack.ingestion.embeddings import get_embeddings_model
from ai_stack.rag_pipeline import generate_rag_response
from pathlib import Path
from ai_stack.config import RAG_SOURCE_PATH

from ai_stack.ingestion.document_identity import (
    gerar_document_id_local,
    calcular_versao_documento
)
CAMINHO = Path(RAG_SOURCE_PATH)
if not CAMINHO.exists() or not CAMINHO.is_dir():
    raise NotADirectoryError(
        f"Diretório inválido: {CAMINHO}"
    )

def main():
    ficheiros = list(CAMINHO.glob("**/*.txt")) + list(CAMINHO.glob("**/*.pdf")) + list(CAMINHO.glob("**/*.md"))
    if not ficheiros:
        raise ValueError(f"Não foram encontrados ficheiros em {CAMINHO}")
    
    for file in ficheiros:
        if not file.is_file():
            raise ValueError(f"O caminho {file} não aponta para um ficheiro válido")
    
    for file in ficheiros:
        if file.suffix.lower() not in [".pdf", ".txt", ".md"]:
            raise ValueError(f"Extensão {file.suffix} é inválida para o ficheiro {file}")

    documentos = []

    for file in ficheiros:
        document_id = gerar_document_id_local(file, CAMINHO)
        document_version = calcular_versao_documento(file)

        docs = reader(
        file,
        document_id,
        document_version
        )

        documentos.extend(docs)
    chunks = chunker(documentos)
    embedding_model = get_embeddings_model()
    db_vector = create_vector_db(chunks, embedding_model)

    resposta = generate_rag_response("o que e Power Query??", db_vector, "intermediario","flashcards")
    
    print("Resposta gerada:")
    print(resposta["answer"])
    print("=="*40)
    dados = db_vector.get(include=["metadatas"])

    print("Total de chunks:", len(dados["ids"]))

    for metadata in dados["metadatas"][:5]:
        print(metadata)
    print("=="*40)
    print("Fonte dos dados:")
    print(resposta["sources"])
    
    
    
if __name__ == "__main__":
    main()