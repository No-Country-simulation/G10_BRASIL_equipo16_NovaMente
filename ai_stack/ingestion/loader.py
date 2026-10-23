from langchain_community.document_loaders import PyMuPDFLoader,TextLoader
from pathlib import Path


def reader(file : Path)->list:
    if not file.exists():
        raise FileNotFoundError(f"Arquivo {file} inexistente")
        
    extensoes = [".pdf",".txt",".md"]
    extensao = file.suffix.lower()

    if extensao not in extensoes:
        raise ValueError(f"Extensão {extensao} é inválida")
        
           
    try:
        if extensao==".pdf":
            leitor =  PyMuPDFLoader(str(file))
              
        else :
            leitor =  TextLoader(str(file), encoding="utf-8")     
        docs = leitor.load()
        for doc in docs:
            doc.metadata["source"] = file.name
            doc.metadata["page"] = doc.metadata.get("page",0) 
        return docs                 
         
    except Exception as e:
        raise RuntimeError(f"Falha ao ler o arquivo {file} : {e}") from e
        