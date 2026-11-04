
from langchain_core.documents import Document


def recuperar_documentos_relevantes(banco_vetorial,pergunta: str,quantidade_documentos: int = 3) -> list[Document]:
    """
    Recupera os documentos mais relevantes para uma pergunta.

    Args:
        banco_vetorial: Base de dados vetorial utilizada na pesquisa.
        pergunta: Pergunta que será utilizada na pesquisa semântica.
        quantidade_documentos: Número máximo de documentos a recuperar.

    Returns:
        Lista de documentos ordenados pela sua relevância.

    Raises:
        ValueError: Quando o banco vetorial não existe,
                    a pergunta está vazia ou a quantidade é inválida.
        TypeError: Quando os parâmetros apresentam tipos incorrectos.
    """

    # 1. Validar a base de dados vetorial
    if banco_vetorial is None:
        raise ValueError("O banco vetorial não pode ser None.")

    # 2. Validar a pergunta
    if not isinstance(pergunta, str):
        raise TypeError("A pergunta deve ser uma string.")

    pergunta_limpa = pergunta.strip()

    if not pergunta_limpa:
        raise ValueError("A pergunta não pode estar vazia.")

    # 3. Validar a quantidade de documentos
    # Em Python, bool também é considerado um subtipo de int.
    if (
        isinstance(quantidade_documentos, bool)
        or not isinstance(quantidade_documentos, int)
    ):
        raise TypeError("A quantidade de documentos deve ser um inteiro.")

    if quantidade_documentos <= 0:
        raise ValueError("A quantidade de documentos deve ser positiva.")

    # 4. Executar a pesquisa por similaridade
    documentos_recuperados = banco_vetorial.similarity_search(
        pergunta_limpa,
        k=quantidade_documentos
    )

    return documentos_recuperados
