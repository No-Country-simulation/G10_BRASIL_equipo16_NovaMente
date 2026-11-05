
from pydantic import ValidationError
import pytest
from unittest.mock import Mock
import ai_stack.agents.reviewer as reviewer



def test_reviewer_aprovado(monkeypatch):

    json_response = """
    {
        "status": "approved",
        "summary": "O conteúdo foi aprovado.",
        "issues": []
    }
    """

    # Simula a resposta do Groq
    def fake_gerar_resposta_llm(messages):
        return json_response

    # Substitui a chamada real ao Groq
    monkeypatch.setattr(
        reviewer,
        "gerar_resposta_llm",
        fake_gerar_resposta_llm
    )

    # Executa o Revisor
    report = reviewer.revisar_conteudo_educativo(
        contexto="O Query Folding traduz transformações para a linguagem da fonte.",
        pacote_educativo={"title": "Quiz sobre Query Folding"},
        perfil="intermediario",
        formato_educativo="quiz"
    )

    # Verifica o resultado
    assert report.status.value == "approved"
    assert report.issues == []


def test_reviewer_com_problemas(monkeypatch):

    json_response = """
    {
        "status": "correction_required",
        "summary": "Foi identificado um erro técnico.",
        "issues": [
            {
                "item_id": "q_001",
                "item_type": "question",
                "category": "technical_accuracy",
                "description": "A definição apresentada está incorreta.",
                "evidence": "O contextoo apresenta uma definição diferente.",
                "suggestion": "Corrigir a definição da pergunta."
            }
        ]
    }
    """

    def fake_gerar_resposta_llm(messages):
        return json_response

    monkeypatch.setattr(
        reviewer,
        "gerar_resposta_llm",
        fake_gerar_resposta_llm
    )

    report = reviewer.revisar_conteudo_educativo(
        contexto="O contextoo apresenta a definição correta.",
        pacote_educativo={"title": "Quiz sobre o tema"},
        perfil="intermediario",
        formato_educativo="quiz"
    )

    assert report.status.value == "correction_required"
    assert len(report.issues) == 1
    assert report.issues[0].item_id == "q_001"
    assert report.issues[0].category.value == "technical_accuracy"


def test_reviewer_json_invalido(monkeypatch):

    def fake_gerar_resposta_llm(messages):
        return "Esta resposta não é um JSON válido."

    monkeypatch.setattr(
        reviewer,
        "gerar_resposta_llm",
        fake_gerar_resposta_llm
    )

    with pytest.raises(ValueError, match="JSON inválido"):
        reviewer.revisar_conteudo_educativo(
            contexto="contextoo de teste.",
            pacote_educativo={"title": "Quiz de teste"},
            perfil="intermediario",
            formato_educativo="quiz"
        )


def test_reviewer_resposta_vazia(monkeypatch):

    def fake_gerar_resposta_llm(messages):
        return ""

    monkeypatch.setattr(
        reviewer,
        "gerar_resposta_llm",
        fake_gerar_resposta_llm
    )

    with pytest.raises(ValueError, match="resposta vazia"):
        reviewer.revisar_conteudo_educativo(
            contexto="contextoo de teste.",
            pacote_educativo={"title": "Quiz de teste"},
            perfil="intermediario",
            formato_educativo="quiz"
        )


def test_reviewer_estrutura_invalida(monkeypatch):

    def fake_gerar_resposta_llm(messages):
        return """
        {
            "status": "accepted",
            "summary": "Conteúdo analisado.",
            "issues": []
        }
        """

    monkeypatch.setattr(
        reviewer,
        "gerar_resposta_llm",
        fake_gerar_resposta_llm
    )

    with pytest.raises(ValidationError):
        reviewer.revisar_conteudo_educativo(
            contexto="contexto de teste.",
            pacote_educativo={"title": "Quiz de teste"},
            perfil="intermediario",
            formato_educativo="quiz"
        )


def test_reviewer_chama_llm(monkeypatch):

    json_response = """
    {
        "status": "approved",
        "summary": "Conteúdo aprovado.",
        "issues": []
    }
    """

    fake_llm = Mock(return_value=json_response)

    monkeypatch.setattr(
        reviewer,
        "gerar_resposta_llm",
        fake_llm
    )

    reviewer.revisar_conteudo_educativo(
        contexto="contexto de teste.",
        pacote_educativo={"title": "Quiz de teste"},
        perfil="intermediario",
        formato_educativo="quiz"
    )

    fake_llm.assert_called_once()


def test_reviewer_envia_dados_corretos(monkeypatch):

    json_response = """
    {
        "status": "approved",
        "summary": "Conteúdo aprovado.",
        "issues": []
    }
    """

    fake_llm = Mock(return_value=json_response)

    monkeypatch.setattr(
        reviewer,
        "gerar_resposta_llm",
        fake_llm
    )

    contextoo = "Query Folding traduz transformações para SQL."
    pacote = {"title": "Quiz sobre Query Folding"}

    reviewer.revisar_conteudo_educativo(
        contexto=contextoo,
        pacote_educativo=pacote,
        perfil="intermediario",
        formato_educativo="quiz"
    )

    messages = fake_llm.call_args.args[0]

    user_message = messages[1]["content"]

    assert contextoo in user_message
    assert "Quiz sobre Query Folding" in user_message
    assert "intermediario" in user_message
    assert "quiz" in user_message