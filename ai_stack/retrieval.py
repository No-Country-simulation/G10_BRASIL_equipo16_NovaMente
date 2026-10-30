
from langchain_core.documents import Document

def retrieve_context_from_db(db_vector, pergunta: str, k: int=3)-> list[Document]:
    if db_vector is None:
        raise ValueError("db_vector não pode estar vazio")

    if not isinstance(pergunta, str):
        raise TypeError("Pergunta deve ser string")

    if not pergunta or pergunta.strip() == "":
        raise ValueError("Pergunta não pode estar vazia ou apenas espaços em branco")
    
    if isinstance(k,bool):
        raise TypeError("k deve ser um inteiro positivo")

    if not isinstance(k, int) :
        raise TypeError("k deve ser um inteiro positivo")
    if k <= 0:
        raise ValueError("k deve ser um inteiro positivo")
    results = db_vector.similarity_search(pergunta.strip(), k=k)
    return results