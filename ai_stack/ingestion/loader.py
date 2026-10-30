
from typing import List
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyMuPDFLoader,
    TextLoader
)


def reader(file: Path,document_id: str,document_version: str) -> List[Document]:

    if not file.exists():
        raise FileNotFoundError(f"Arquivo {file} inexistente")

    if not file.is_file():
        raise ValueError(f"{file} não é um arquivo válido")

    if not isinstance(document_id, str) or not document_id.strip():
        raise ValueError("document_id inválido")

    if not isinstance(document_version, str) or not document_version.strip():
        raise ValueError("document_version inválido")

    extensao = file.suffix.lower()

    if extensao not in [".pdf", ".txt", ".md"]:
        raise ValueError(f"Extensão {extensao} inválida")

    if extensao == ".pdf":
        leitor = PyMuPDFLoader(str(file))
    else:
        leitor = TextLoader(str(file), encoding="utf-8")

    docs = leitor.load()

    for doc in docs:
        doc.metadata.update({
            "source": file.name,
            "document_id": document_id,
            "document_version": document_version
        })

    return docs
