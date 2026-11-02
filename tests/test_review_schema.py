from pydantic import ValidationError
import pytest
from ai_stack.schemas import ReviewReport


def test_review_aprovado():
    dados = {
    "status": "approved",
    "summary": "Foi aprovado",
    "issues": [    ]

   
}
    dados_validos = ReviewReport.model_validate(dados)

def test_review_com_problemas():
    dados = {
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
    dados_validos = ReviewReport.model_validate(dados)


def test_categoria_invalida():
    dados = {
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
        ReviewReport.model_validate(dados)

def test_status_invalido():
    dados = {
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
        ReviewReport.model_validate(dados)

def test_aprovado_com_problemas():
    dados = {
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
        ReviewReport.model_validate(dados)

def test_correcao_sem_problemas():
    dados = {
        "status": "correction_required",
        "summary": "Foi identificado um erro técnico.",
        "issues": [ ]
    }
    with pytest.raises(ValidationError):
        ReviewReport.model_validate(dados)