
import ai_stack.rag_pipeline as modulo_pipeline

from langchain_core.documents import Document
from pydantic import ValidationError
from unittest.mock import Mock

import pytest

from ai_stack.schemas import ReviewReport, ReviewStatus


def test_deve_gerar_flashcards_validos(monkeypatch):

    documento_fonte = Document(
        page_content="O Power Query permite transformar dados.",
        metadata={
            "source": "1 - Guia de Power BI do Power Query ao DAX avançado (PL-300).md",
            "page": 0
        }
    )

    monkeypatch.setattr(
        modulo_pipeline,
        "recuperar_documentos_relevantes",
        lambda *argumentos, **argumentos_nomeados: [documento_fonte]
    )

    resposta_llm_json = """
    {
        "metadata": {
            "profile_applied": "intermediario",
            "format_generated": "flashcards",
            "key_concepts": ["Power Query"],
            "study_time_minutes": 5,
            "prerequisites": []
        },
        "content": {
            "title": "Introdução ao Power Query",
            "cards": [
                {
                    "card_id": "card_001",
                    "front": "O que é o Power Query?",
                    "back": "É uma ferramenta para transformar dados."
                }
            ]
        }
    }
    """

    monkeypatch.setattr(
        modulo_pipeline,
        "gerar_resposta_llm",
        lambda *argumentos, **argumentos_nomeados: resposta_llm_json
    )

    mock_revisor = Mock(
        return_value=ReviewReport(
            status=ReviewStatus.approved,
            summary="Conteúdo aprovado.",
            issues=[]
        )
    )

    monkeypatch.setattr(
        modulo_pipeline,
        "revisar_conteudo_educativo",
        mock_revisor
    )

    retorno_pipeline = modulo_pipeline.gerar_resposta_rag(
        "Power Query",
        None,
        "intermediario",
        "flashcards"
    )

    mock_revisor.assert_called_once()

    assert retorno_pipeline["review_report"]["status"] == "approved"

    assert "answer" in retorno_pipeline
    assert "sources" in retorno_pipeline

    assert retorno_pipeline["answer"]["metadata"]["profile_applied"] == "intermediario"
    assert retorno_pipeline["answer"]["metadata"]["format_generated"] == "flashcards"

    assert len(retorno_pipeline["answer"]["content"]["cards"]) > 0

    assert retorno_pipeline["sources"][0]["source"] == documento_fonte.metadata["source"]


def test_deve_rejeitar_json_invalido(monkeypatch):

    documento_fonte = Document(
        page_content="O Power Query permite transformar dados.",
        metadata={
            "source": "2 - manual-pl300-preparacao-modelagem-dax.md",
            "page": 0
        }
    )

    monkeypatch.setattr(
        modulo_pipeline,
        "recuperar_documentos_relevantes",
        lambda *argumentos, **argumentos_nomeados: [documento_fonte]
    )

    resposta_llm_json = """
    {
        "metadata":
            "profile_applied": "intermediario",
            "format_generated": "flashcards",
            "key_concepts": ["Power Query"],
            "study_time_minutes": 5,
            "prerequisites": []
        },
        "content": {
            "title": "Introdução ao Power Query",
            "cards": [
                {
                    "front": "O que é o Power Query?",
                    "back": "É uma ferramenta para transformar dados."
                }
            ]
        }
    }
    """

    monkeypatch.setattr(
        modulo_pipeline,
        "gerar_resposta_llm",
        lambda *argumentos, **argumentos_nomeados: resposta_llm_json
    )

    with pytest.raises(ValueError):
        modulo_pipeline.gerar_resposta_rag(
            "Power Query",
            None,
            "intermediario",
            "flashcards"
        )


def test_deve_rejeitar_estrutura_invalida(monkeypatch):

    documento_fonte = Document(
        page_content="O Power Query permite transformar dados.",
        metadata={
            "source": "2 - manual-pl300-preparacao-modelagem-dax.md",
            "page": 0
        }
    )

    monkeypatch.setattr(
        modulo_pipeline,
        "recuperar_documentos_relevantes",
        lambda *argumentos, **argumentos_nomeados: [documento_fonte]
    )

    resposta_llm_json = """
    {
        "metadata": {
            "profile_applied": "intermediario",
            "format_generated": "flashcards",
            "key_concepts": ["Power Query"],
            "study_time_minutes": 5,
            "prerequisites": []
        },
        "content": {
            "title": "Introdução ao Power Query",
            "cards": []
        }
    }
    """

    monkeypatch.setattr(
        modulo_pipeline,
        "gerar_resposta_llm",
        lambda *argumentos, **argumentos_nomeados: resposta_llm_json
    )

    with pytest.raises(ValidationError):
        modulo_pipeline.gerar_resposta_rag(
            "Power Query",
            None,
            "intermediario",
            "flashcards"
        )


def test_deve_gerar_tutorial_valido(monkeypatch):

    documento_fonte = Document(
        page_content="O Power Query permite transformar dados.",
        metadata={
            "source": "2 - manual-pl300-preparacao-modelagem-dax.md",
            "page": 0
        }
    )

    monkeypatch.setattr(
        modulo_pipeline,
        "recuperar_documentos_relevantes",
        lambda *argumentos, **argumentos_nomeados: [documento_fonte]
    )

    resposta_llm_json = """
    {
        "metadata": {
            "profile_applied": "intermediario",
            "format_generated": "tutorial",
            "key_concepts": [
                "Power Query",
                "transformação de dados",
                "ETL"
            ],
            "study_time_minutes": 5,
            "prerequisites": []
        },
        "content": {
            "title": "Introdução ao Power Query",
            "introduction": "O Power Query permite importar, limpar e transformar dados antes de os utilizar em análises.",
            "steps": [
                {
                    "title": "Compreender a finalidade",
                    "explanation": "O Power Query é utilizado para preparar dados, permitindo transformar a sua estrutura antes da análise.",
                    "example": "Remover colunas desnecessárias de uma tabela antes de utilizar os dados."
                },
                {
                    "title": "Transformar os dados",
                    "explanation": "As transformações permitem modificar os dados para que fiquem adequados às necessidades da análise.",
                    "example": "Alterar o tipo de uma coluna para que os valores sejam interpretados como números."
                }
            ]
        }
    }
    """

    monkeypatch.setattr(
        modulo_pipeline,
        "gerar_resposta_llm",
        lambda *argumentos, **argumentos_nomeados: resposta_llm_json
    )

    mock_revisor = Mock()

    monkeypatch.setattr(
        modulo_pipeline,
        "revisar_conteudo_educativo",
        mock_revisor
    )

    retorno_pipeline = modulo_pipeline.gerar_resposta_rag(
        "Power Query",
        None,
        "intermediario",
        "tutorial"
    )

    mock_revisor.assert_not_called()

    assert "answer" in retorno_pipeline
    assert "sources" in retorno_pipeline

    assert retorno_pipeline["answer"]["metadata"]["profile_applied"] == "intermediario"
    assert retorno_pipeline["answer"]["metadata"]["format_generated"] == "tutorial"

    assert "steps" in retorno_pipeline["answer"]["content"]
    assert len(retorno_pipeline["answer"]["content"]["steps"]) > 0

    assert retorno_pipeline["sources"][0]["source"] == documento_fonte.metadata["source"]


def test_deve_retornar_contexto_insuficiente_sem_chamar_llm(monkeypatch):

    monkeypatch.setattr(
        modulo_pipeline,
        "recuperar_documentos_relevantes",
        lambda *argumentos, **argumentos_nomeados: []
    )

    mock_llm = Mock()

    monkeypatch.setattr(
        modulo_pipeline,
        "gerar_resposta_llm",
        mock_llm
    )

    retorno_pipeline = modulo_pipeline.gerar_resposta_rag(
        "Power Query",
        None,
        "intermediario",
        "tutorial"
    )

    assert retorno_pipeline["status"] == "insufficient_context"
    assert retorno_pipeline["answer"] is None
    assert retorno_pipeline["sources"] == []
    assert retorno_pipeline["message"] == "Não foram encontrados documentos relevantes."

    mock_llm.assert_not_called()


def test_deve_gerar_quiz_valido(monkeypatch):

    documento_fonte = Document(
        page_content="Query Folding traduz os passos do Power Query para a linguagem da fonte, como SQL.",
        metadata={
            "source": "manual-power-bi.pdf",
            "page": 3
        }
    )

    monkeypatch.setattr(
        modulo_pipeline,
        "recuperar_documentos_relevantes",
        lambda *argumentos, **argumentos_nomeados: [documento_fonte]
    )

    resposta_llm_json = """
    {
        "metadata": {
            "profile_applied": "intermediario",
            "format_generated": "quiz",
            "key_concepts": ["Query Folding", "Power Query"],
            "study_time_minutes": 5,
            "prerequisites": []
        },
        "content": {
            "title": "Quiz sobre Query Folding",
            "questions": [
                {
                    "question_id": "q_001",
                    "question": "O que é Query Folding?",
                    "options": [
                        {
                            "option_id": "A",
                            "text": "Traduzir passos de transformação para a linguagem da fonte."
                        },
                        {
                            "option_id": "B",
                            "text": "Armazenar dados permanentemente em memória."
                        }
                    ],
                    "correct_option_id": "A",
                    "justification": "O contexto explica que os passos são traduzidos para a linguagem da fonte."
                }
            ]
        }
    }
    """

    monkeypatch.setattr(
        modulo_pipeline,
        "gerar_resposta_llm",
        lambda *argumentos, **argumentos_nomeados: resposta_llm_json
    )

    mock_revisor = Mock(
        return_value=ReviewReport(
            status=ReviewStatus.approved,
            summary="Quiz aprovado.",
            issues=[]
        )
    )

    monkeypatch.setattr(
        modulo_pipeline,
        "revisar_conteudo_educativo",
        mock_revisor
    )

    retorno_pipeline = modulo_pipeline.gerar_resposta_rag(
        "O que é Query Folding?",
        None,
        "intermediario",
        "quiz"
    )

    assert "answer" in retorno_pipeline
    assert "review_report" in retorno_pipeline

    assert retorno_pipeline["answer"]["metadata"]["format_generated"] == "quiz"
    assert len(retorno_pipeline["answer"]["content"]["questions"]) == 1

    assert retorno_pipeline["review_report"]["status"] == "approved"

    mock_revisor.assert_called_once()
