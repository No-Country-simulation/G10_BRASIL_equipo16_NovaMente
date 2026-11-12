import pytest

from src.adaptador import RespostaInvalidaError, adaptar_resposta
from src.modelos import Flashcard, PassoTutorial, QuestaoQuiz


def test_flashcards(resposta_flashcards):
    r = adaptar_resposta(resposta_flashcards)
    assert r.status == "success"
    assert r.pacote.metadados.formato == "flashcards"
    assert len(r.pacote.itens) == 5
    assert all(isinstance(i, Flashcard) for i in r.pacote.itens)
    assert r.revisao is not None and r.revisao.aprovado
    assert r.fontes[0].arquivo.endswith(".md")


def test_quiz_resposta_correta_resolvida(resposta_quiz):
    r = adaptar_resposta(resposta_quiz)
    q = r.pacote.itens[0]
    assert isinstance(q, QuestaoQuiz)
    assert q.resposta_correta.id == q.id_correta
    assert q.resposta_correta.texto == "A tabela fato"


def test_tutorial_sem_revisao(resposta_tutorial):
    r = adaptar_resposta(resposta_tutorial)
    assert all(isinstance(i, PassoTutorial) for i in r.pacote.itens)
    assert r.pacote.introducao
    assert r.pacote.itens[1].exemplo.startswith("Total Vendas")
    assert r.revisao is None


def test_sem_contexto(resposta_sem_contexto):
    r = adaptar_resposta(resposta_sem_contexto)
    assert r.status == "insufficient_context"
    assert r.pacote is None
    assert "relevantes" in r.mensagem


def test_requires_manual_review_traz_relatorio(resposta_quiz):
    resposta_quiz["status"] = "requires_manual_review"
    resposta_quiz["answer"] = None
    resposta_quiz["review_report"] = {
        "status": "correction_required",
        "summary": "Pergunta 2 sem suporte no contexto.",
        "issues": [{"item_id": "q_002", "item_type": "question", "category": "source_fidelity",
                    "description": "x", "evidence": "y", "suggestion": "z"}],
    }
    r = adaptar_resposta(resposta_quiz)
    assert r.pacote is None
    assert not r.revisao.aprovado
    assert r.revisao.problemas[0].categoria == "source_fidelity"


@pytest.mark.parametrize("quebra", [
    lambda d: d.pop("status"),
    lambda d: d.update(status="whatever"),
    lambda d: d["answer"].pop("content"),
    lambda d: d["answer"]["content"]["cards"][0].pop("front"),
    lambda d: d["answer"]["metadata"].update(format_generated="resumo"),
])
def test_respostas_malformadas(resposta_flashcards, quebra):
    quebra(resposta_flashcards)
    with pytest.raises(RespostaInvalidaError):
        adaptar_resposta(resposta_flashcards)
