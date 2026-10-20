from langchain_community.document_loaders import PyMuPDFLoader,TextLoader
from pathlib import Path


def reader(file : Path)->list:
    extensoes = [".pdf",".txt",".md"]
    extensao = file.suffix.lower()
    
    if extensao not in extensoes:
        return []
        
    if not file.exists():
        return []
        
    if extensao==".pdf":
        leitor =  PyMuPDFLoader(str(file))
        
    else :
        leitor =  TextLoader(str(file), encoding="utf-8")
    
    return leitor.load()
    