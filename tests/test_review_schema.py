
from pydantic import ValidationError
import pytest

from ai_stack.schemas import ReviewReport


def test_deve_validar_relatorio_aprovado():
    dados_revisao = {
        "status": "approved",
        "summary": "Foi aprovado",
        "issues": []
    }

    relatorio_validado = ReviewReport.model_validate(dados_revisao)


def test_deve_validar_relatorio_com_problemas():
    dados_revisao = {
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

    relatorio_validado = ReviewReport.model_validate(dados_revisao)


def test_deve_rejeitar_categoria_invalida():
    dados_revisao = {
        "status": "correction_required",
        "summary": "Foi identificado um erro técnico.",
        "issues": [
            {
                "item_id": "q_001",
                "item_type": "question",
                "category": "wrong_answer",
                "description": "A definição apresentada está incorreta.",
                "evidence": "O contexto apresenta uma definição diferente.",
                "suggestion": "Corrigir a definição da pergunta."
            }
        ]
    }

    with pytest.raises(ValidationError):
        ReviewReport.model_validate(dados_revisao)


def test_deve_rejeitar_status_invalido():
    dados_revisao = {
        "status": "accepted",
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

    with pytest.raises(ValidationError):
        ReviewReport.model_validate(dados_revisao)


def test_deve_rejeitar_relatorio_aprovado_com_problemas():
    dados_revisao = {
        "status": "approved",
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

    with pytest.raises(ValidationError):
        ReviewReport.model_validate(dados_revisao)


def test_deve_rejeitar_correcao_sem_problemas():
    dados_revisao = {
        "status": "correction_required",
        "summary": "Foi identificado um erro técnico.",
        "issues": []
    }

    with pytest.raises(ValidationError):
        ReviewReport.model_validate(dados_revisao)
