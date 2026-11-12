import json
from pathlib import Path

import pytest

from src.adaptador import adaptar_resposta
from src.config import PASTA_FIXTURES
from src.modelos import Requisicao


def _fixture(nome: str) -> dict:
    return json.loads((PASTA_FIXTURES / nome).read_text(encoding="utf-8"))


@pytest.fixture
def resposta_flashcards() -> dict:
    return _fixture("flashcards_iniciante.json")


@pytest.fixture
def resposta_quiz() -> dict:
    return _fixture("quiz_intermediario.json")


@pytest.fixture
def resposta_tutorial() -> dict:
    return _fixture("tutorial_iniciante.json")


@pytest.fixture
def resposta_sem_contexto() -> dict:
    return _fixture("sem_contexto.json")


@pytest.fixture
def requisicao() -> Requisicao:
    return Requisicao(pergunta="O que é o Power Query?", perfil="iniciante", formato="flashcards",
                      nome_arquivo="guia.md", titulo_documento="guia")


@pytest.fixture
def resultado_quiz(resposta_quiz):
    return adaptar_resposta(resposta_quiz)


@pytest.fixture
def pasta_tmp(tmp_path: Path) -> Path:
    return tmp_path
