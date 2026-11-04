
from typing import List
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader
)


def carregar_documento(
    caminho_arquivo: Path,
    id_documento: str,
    versao_documento: str
) -> List[Document]:

    if not caminho_arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo {caminho_arquivo} inexistente"
        )

    if not caminho_arquivo.is_file():
        raise ValueError(
            f"{caminho_arquivo} não é um arquivo válido"
        )

    if not isinstance(id_documento, str) or not id_documento.strip():
        raise ValueError("document_id inválido")

    if not isinstance(versao_documento, str) or not versao_documento.strip():
        raise ValueError("document_version inválido")

    extensao = caminho_arquivo.suffix.lower()

    if extensao not in [".pdf", ".txt", ".md"]:
        raise ValueError(f"Extensão {extensao} inválida")

    if extensao == ".pdf":
        leitor = PyMuPDFLoader(str(caminho_arquivo))
    else:
        leitor = TextLoader(str(caminho_arquivo), encoding="utf-8")

    documentos = leitor.load()

    for documento in documentos:
        documento.metadata.update({
            "source": caminho_arquivo.name,
            "document_id": id_documento,
            "document_version": versao_documento
        })

    return documentos
