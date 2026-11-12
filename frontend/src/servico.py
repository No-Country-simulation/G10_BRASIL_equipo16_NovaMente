"""Interface comum dos serviços de geração (mock e ai_stack)."""

from typing import Protocol


class ErroServico(Exception):
    """Erro já traduzido para uma mensagem que pode ser mostrada ao usuário."""


class ServicoConteudo(Protocol):
    nome: str

    def indexar(self, nome_arquivo: str, dados: bytes) -> str:
        """Indexa um documento enviado pelo usuário. Devolve um rótulo do documento."""
        ...

    def gerar(self, pergunta: str, perfil: str, formato: str) -> dict:
        """Devolve o dicionário bruto no formato de `generate_rag_response`."""
        ...
