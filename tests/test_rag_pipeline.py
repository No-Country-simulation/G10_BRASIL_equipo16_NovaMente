import ai_stack.rag_pipeline as pipeline
from langchain_core.documents import Document
from pydantic import ValidationError
import pytest
from unittest.mock import Mock
from ai_stack.schemas import ReviewReport, ReviewStatus
def test_flashcards_validos(monkeypatch):
    doc =Document(
    page_content="O Power Query permite transformar dados.",
    metadata={"source": "1 - Guia de Power BI do Power Query ao DAX avançado (PL-300).md", "page": 0}
    )
    monkeypatch.setattr(
    pipeline,
    "retrieve_context_from_db",
    lambda *args, **kwargs: [doc]
)
    resposta_json = """
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
            {   "card_id": "card_001",
                "front": "O que é o Power Query?",
                "back": "É uma ferramenta para transformar dados."
            }
        ]
    }
}
"""
    monkeypatch.setattr(
    pipeline,
    "generate_completion",
    lambda *args, **kwargs: resposta_json
)

    review_mock = Mock(
    return_value=ReviewReport(
    status=ReviewStatus.approved,
        summary="Conteúdo aprovado.",
        issues=[]
    )
)

    monkeypatch.setattr(
        pipeline,
        "review_educational_content",
        review_mock
    )

    resultado = pipeline.generate_rag_response("Power Query",None,"intermediario","flashcards")

    review_mock.assert_called_once()

    assert resultado["review_report"]["status"] == "approved"

    assert "answer" in resultado
    assert "sources" in resultado

    assert resultado["answer"]["metadata"]["profile_applied"] == "intermediario"
    assert resultado["answer"]["metadata"]["format_generated"] == "flashcards"

    assert len(resultado["answer"]["content"]["cards"]) > 0

    assert resultado["sources"][0]["source"] == doc.metadata["source"]



def test_json_invalido(monkeypatch):
   doc =Document(
       page_content="O Power Query permite transformar dados.",
       metadata={"source": "2 - manual-pl300-preparacao-modelagem-dax.md", "page": 0}
       )
   monkeypatch.setattr(
        pipeline,
        "retrieve_context_from_db",
        lambda *args, **kwargs: [doc]
    )
   resposta_json = """
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
    pipeline,
    "generate_completion",
    lambda *args, **kwargs: resposta_json
    )
    
    # 4. Usar
   with pytest.raises(ValueError):
      pipeline.generate_rag_response(
        "Power Query",
        None,
        "intermediario",
        "flashcards"
    )
      
def test_estrutura_invalida(monkeypatch):
   doc =Document(
       page_content="O Power Query permite transformar dados.",
       metadata={"source": "2 - manual-pl300-preparacao-modelagem-dax.md", "page": 0}
       )
   monkeypatch.setattr(
        pipeline,
        "retrieve_context_from_db",
        lambda *args, **kwargs: [doc]
    )
   resposta_json = """
    {
    "metadata":{  
       "profile_applied": "intermediario",
       "format_generated": "flashcards",
       "key_concepts": ["Power Query"],
       "study_time_minutes": 5,
       "prerequisites": []
    },
    "content": {
       "title": "Introdução ao Power Query",
       "cards": [
       ]
    }
    }
    """
   monkeypatch.setattr(
    pipeline,
    "generate_completion",
    lambda *args, **kwargs: resposta_json
    )
   with pytest.raises(ValidationError):
          pipeline.generate_rag_response(
            "Power Query",
            None,
            "intermediario",
            "flashcards"
        )

def test_tutorial_valido(monkeypatch):

    doc =Document(
        page_content="O Power Query permite transformar dados.",
        metadata={"source": "2 - manual-pl300-preparacao-modelagem-dax.md", "page": 0}
        )
    monkeypatch.setattr(
         pipeline,
         "retrieve_context_from_db",
         lambda *args, **kwargs: [doc]
     )
    resposta_json = """
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
     pipeline,
     "generate_completion",
     lambda *args, **kwargs: resposta_json
     )
    review_mock = Mock()

    monkeypatch.setattr(
        pipeline,
        "review_educational_content",
        review_mock
    )

    resultado = pipeline.generate_rag_response(
         "Power Query",
         None,
         "intermediario",
         "tutorial"
     )

    review_mock.assert_not_called()
    
    assert "answer" in resultado
    assert "sources" in resultado
    
    assert resultado["answer"]["metadata"]["profile_applied"] == "intermediario"
    assert resultado["answer"]["metadata"]["format_generated"] == "tutorial"
    
    assert "steps" in resultado["answer"]["content"]
    assert len(resultado["answer"]["content"]["steps"]) > 0
    
    assert resultado["sources"][0]["source"] == doc.metadata["source"]


def test_sem_contexto( monkeypatch):
    monkeypatch.setattr(
    pipeline,
    "retrieve_context_from_db",
    lambda *args, **kwargs: []
)

    llm_mock = Mock()

    monkeypatch.setattr(
    pipeline,
    "generate_completion",
    llm_mock
)   
    
    resultado = pipeline.generate_rag_response(
             "Power Query",
             None,
             "intermediario",
             "tutorial"
         )
    assert resultado["status"]== "insufficient_context"



    assert resultado["answer"] is None



    assert resultado["sources"] == []
    assert resultado["message"] == "Não foram encontrados documentos relevantes."



    llm_mock.assert_not_called()

def test_quiz_valido(monkeypatch):

    doc = Document(
        page_content="Query Folding traduz os passos do Power Query para a linguagem da fonte, como SQL.",
        metadata={"source": "manual-power-bi.pdf", "page": 3}
    )

    monkeypatch.setattr(
        pipeline,
        "retrieve_context_from_db",
        lambda *args, **kwargs: [doc]
    )

    resposta_json = """
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
        pipeline,
        "generate_completion",
        lambda *args, **kwargs: resposta_json
    )

    review_mock = Mock(
        return_value=ReviewReport(
            status=ReviewStatus.approved,
            summary="Quiz aprovado.",
            issues=[]
        )
    )

    monkeypatch.setattr(
        pipeline,
        "review_educational_content",
        review_mock
    )

    resultado = pipeline.generate_rag_response(
        "O que é Query Folding?",
        None,
        "intermediario",
        "quiz"
    )

    assert "answer" in resultado
    assert "review_report" in resultado

    assert resultado["answer"]["metadata"]["format_generated"] == "quiz"
    assert len(resultado["answer"]["content"]["questions"]) == 1

    assert resultado["review_report"]["status"] == "approved"

    review_mock.assert_called_once()