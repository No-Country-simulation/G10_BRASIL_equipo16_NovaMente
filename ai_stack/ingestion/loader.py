from typing import List
from langchain_core.documents import Document

from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from pathlib import Path

def reader(file: Path) ->List[Document]:
    if not file.exists():
        raise FileNotFoundError(f"Arquivo {file} inexistente")
    if not file.is_file():
        raise ValueError(f"O caminho {file} não aponta para um arquivo válido")
    extensao = file.suffix.lower()
    if extensao not in [".pdf",".txt",".md"]:
        raise ValueError(f"Extensão {extensao} é inválida")
           
    
    if extensao == ".pdf":
            leitor = PyMuPDFLoader(str(file))
    else:
            leitor = TextLoader(str(file), encoding="utf-8")
    docs = leitor.load()
    for doc in docs:
        doc.metadata["source"] = file.name
        if doc.metadata.get("page", None) is None:
             doc.metadata["page"] =0
    return docs                 
    