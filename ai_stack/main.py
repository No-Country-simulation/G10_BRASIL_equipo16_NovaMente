from ai_stack.ingestion.loader import reader
from ai_stack.ingestion.chunking import chunker
from ai_stack.ingestion.vector_store import create_vector_db
from ai_stack.ingestion.embeddings import get_embeddings_model
from ai_stack.rag_pipeline import generate_rag_response
from pathlib import Path
from ai_stack.config import RAG_SOURCE_PATH
from ai_stack.retrieval import retrieve_context_from_db
CAMINHO = Path(RAG_SOURCE_PATH)
if not CAMINHO:
    raise ValueError(f"Caminho {RAG_SOURCE_PATH} não é válido")


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
        docs = reader(file)
        documentos.extend(docs)
    chunks = chunker(documentos)
    embedding_model = get_embeddings_model()
    db_vector = create_vector_db(chunks, embedding_model)
    resposta = generate_rag_response("o que e Power Query??", db_vector)
    print("Resposta gerada:")
    print(resposta["answer"])
    resultados = retrieve_context_from_db(db_vector, "o que e Power Query??", k=3)
    print("Resultados da pesquisa:")
    for i, doc in enumerate(resultados):
        print(f"Resultado {i + 1}:")
        print(f"Conteúdo: {doc.page_content}")
        print(f"Metadados: {doc.metadata}")
        print("-" * 40)
if __name__ == "__main__":
    main()