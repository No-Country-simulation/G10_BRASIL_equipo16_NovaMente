"""Serviço de demonstração: devolve fixtures sem carregar modelo nem chamar LLM."""

import json
import time
from pathlib import Path

from src.config import EXTENSOES_SUPORTADAS, PASTA_FIXTURES
from src.servico import ErroServico

FIXTURE_POR_FORMATO = {
    "flashcards": "flashcards_iniciante.json",
    "quiz": "quiz_intermediario.json",
    "tutorial": "tutorial_iniciante.json",
}


class ServicoMock:
    nome = "demonstração (sem IA)"

    def __init__(self, pasta_fixtures: Path = PASTA_FIXTURES, atraso_segundos: float = 1.0) -> None:
        self.pasta_fixtures = pasta_fixtures
        self.atraso_segundos = atraso_segundos

    def indexar(self, nome_arquivo: str, dados: bytes) -> str:
        if not nome_arquivo.lower().endswith(EXTENSOES_SUPORTADAS):
            raise ErroServico(f"Arquivo não suportado. Use {', '.join(EXTENSOES_SUPORTADAS)}.")
        if not dados:
            raise ErroServico("O arquivo enviado está vazio.")
        return nome_arquivo

    def gerar(self, pergunta: str, perfil: str, formato: str) -> dict:
        if not pergunta.strip():
            raise ErroServico("Digite o tema ou a pergunta que o material deve cobrir.")
        time.sleep(self.atraso_segundos)
        if "nada" in pergunta.lower():  # atalho para testar a tela de "sem contexto"
            return self._ler("sem_contexto.json")
        nome = FIXTURE_POR_FORMATO.get(formato)
        if nome is None:
            raise ErroServico(f"Formato '{formato}' ainda não é suportado.")
        resposta = self._ler(nome)
        # a fixture tem um perfil fixo; refletir o perfil pedido para a demo fazer sentido
        resposta["answer"]["metadata"]["profile_applied"] = perfil
        return resposta

    def _ler(self, nome: str) -> dict:
        return json.loads((self.pasta_fixtures / nome).read_text(encoding="utf-8"))
