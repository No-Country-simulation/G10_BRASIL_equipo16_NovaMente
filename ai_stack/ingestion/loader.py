from langchain_community.document_loaders import PyMuPDFLoader,TextLoader
from pathlib import Path


def reader(file : Path)->list:
    extensoes = [".pdf",".txt",".md"]
    extensao = file.suffix.lower()
    
    if extensao not in extensoes:
        raise ValueError(f"Extensão {extensao} é inválida")
        
    if not file.exists():
        raise FileNotFoundError(f"Arquivo {file} inexistente")
        
    try:
        if extensao==".pdf":
            leitor =  PyMuPDFLoader(str(file)) 
        else :
            leitor =  TextLoader(str(file), encoding="utf-8")     
        return leitor.load()
    
    except Exception as e:
        raise RuntimeError(f"Falha ao ler o arquivo {file} : {e}") from e
        