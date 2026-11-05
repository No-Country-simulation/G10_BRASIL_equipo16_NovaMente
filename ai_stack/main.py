import json
from ai_stack.ingestion.loader import carregar_documento
from ai_stack.ingestion.chunking import dividir_documentos_em_blocos
from ai_stack.ingestion.vector_store import criar_banco_vetorial
from ai_stack.ingestion.embeddings import obter_modelo_embeddings
from ai_stack.rag_pipeline import gerar_resposta_rag
from pathlib import Path
from ai_stack.config import RAG_SOURCE_PATH

from ai_stack.ingestion.document_identity import (
    gerar_identificador_documento_local,
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
        document_id = gerar_identificador_documento_local(file, CAMINHO)
        document_version = calcular_versao_documento(file)

        docs = carregar_documento(
        file,
        document_id,
        document_version
        )

        documentos.extend(docs)
    chunks = dividir_documentos_em_blocos(documentos)
    embedding_model = obter_modelo_embeddings()
    db_vector = criar_banco_vetorial(chunks, embedding_model)

    resposta = gerar_resposta_rag("o que e Power Query??", db_vector, "intermediario","flashcards")
    
    print("\n=== RESULTADO DO PIPELINE ===")

    print("Estado:", resposta.get("status"))
    print("Mensagem:", resposta.get("message"))

    print("\n=== RELATÓRIO DO REVIEWER ===")

    relatorio = resposta.get("review_report")

    if relatorio is None:
        print("Nenhum relatório de revisão foi devolvido.")

    elif isinstance(relatorio, dict):
        print(json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
            default=str
        ))

    elif hasattr(relatorio, "model_dump"):
        print(json.dumps(
            relatorio.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
            default=str
        ))

    else:
        print(relatorio)

    print("\n=== CONTEÚDO GERADO ===")
    print(resposta.get("answer"))

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