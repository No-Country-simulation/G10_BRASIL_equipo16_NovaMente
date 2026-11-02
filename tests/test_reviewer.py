
from pydantic import ValidationError
import pytest
from unittest.mock import Mock
import ai_stack.agents.reviewer as reviewer



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
    def fake_generate_completion(messages):
        return json_response

    # Substitui a chamada real ao Groq
    monkeypatch.setattr(
        reviewer,
        "generate_completion",
        fake_generate_completion
    )

    # Executa o Revisor
    report = reviewer.review_educational_content(
        context="O Query Folding traduz transformações para a linguagem da fonte.",
        educational_package={"title": "Quiz sobre Query Folding"},
        profile="intermediario",
        educational_format="quiz"
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
                "evidence": "O contexto apresenta uma definição diferente.",
                "suggestion": "Corrigir a definição da pergunta."
            }
        ]
    }
    """

    def fake_generate_completion(messages):
        return json_response

    monkeypatch.setattr(
        reviewer,
        "generate_completion",
        fake_generate_completion
    )

    report = reviewer.review_educational_content(
        context="O contexto apresenta a definição correta.",
        educational_package={"title": "Quiz sobre o tema"},
        profile="intermediario",
        educational_format="quiz"
    )

    assert report.status.value == "correction_required"
    assert len(report.issues) == 1
    assert report.issues[0].item_id == "q_001"
    assert report.issues[0].category.value == "technical_accuracy"


def test_reviewer_json_invalido(monkeypatch):

    def fake_generate_completion(messages):
        return "Esta resposta não é um JSON válido."

    monkeypatch.setattr(
        reviewer,
        "generate_completion",
        fake_generate_completion
    )

    with pytest.raises(ValueError, match="JSON inválido"):
        reviewer.review_educational_content(
            context="Contexto de teste.",
            educational_package={"title": "Quiz de teste"},
            profile="intermediario",
            educational_format="quiz"
        )


def test_reviewer_resposta_vazia(monkeypatch):

    def fake_generate_completion(messages):
        return ""

    monkeypatch.setattr(
        reviewer,
        "generate_completion",
        fake_generate_completion
    )

    with pytest.raises(ValueError, match="resposta vazia"):
        reviewer.review_educational_content(
            context="Contexto de teste.",
            educational_package={"title": "Quiz de teste"},
            profile="intermediario",
            educational_format="quiz"
        )


def test_reviewer_estrutura_invalida(monkeypatch):

    def fake_generate_completion(messages):
        return """
        {
            "status": "accepted",
            "summary": "Conteúdo analisado.",
            "issues": []
        }
        """

    monkeypatch.setattr(
        reviewer,
        "generate_completion",
        fake_generate_completion
    )

    with pytest.raises(ValidationError):
        reviewer.review_educational_content(
            context="Contexto de teste.",
            educational_package={"title": "Quiz de teste"},
            profile="intermediario",
            educational_format="quiz"
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
        "generate_completion",
        fake_llm
    )

    reviewer.review_educational_content(
        context="Contexto de teste.",
        educational_package={"title": "Quiz de teste"},
        profile="intermediario",
        educational_format="quiz"
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
        "generate_completion",
        fake_llm
    )

    contexto = "Query Folding traduz transformações para SQL."
    pacote = {"title": "Quiz sobre Query Folding"}

    reviewer.review_educational_content(
        context=contexto,
        educational_package=pacote,
        profile="intermediario",
        educational_format="quiz"
    )

    messages = fake_llm.call_args.args[0]

    user_message = messages[1]["content"]

    assert contexto in user_message
    assert "Quiz sobre Query Folding" in user_message
    assert "intermediario" in user_message
    assert "quiz" in user_message