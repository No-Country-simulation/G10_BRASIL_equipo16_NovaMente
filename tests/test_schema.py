
from pydantic import ValidationError
import pytest

from ai_stack.schemas import (
    EducationalPackage,
    FlashcardContent,
    TutorialContent,
    QuizContent,
    QuizQuestion,
)


def test_deve_validar_pacote_de_flashcards():
    dados_pacote = {
        "metadata": {
            "profile_applied": "iniciante",
            "format_generated": "flashcards",
            "key_concepts": ["SQL"],
            "study_time_minutes": 4,
            "prerequisites": ["Banco de dados"]
        },
        "content": {
            "title": "Banco de dados",
            "cards": [
                {
                    "card_id": "card_001",
                    "front": "O que quer dizer SQL?",
                    "back": "Structured Query Language"
                }
            ]
        }
    }

    pacote_validado = EducationalPackage.model_validate(dados_pacote)

    assert isinstance(pacote_validado, EducationalPackage)
    assert isinstance(pacote_validado.content, FlashcardContent)


def test_deve_validar_pacote_de_tutorial():
    dados_pacote = {
        "metadata": {
            "profile_applied": "iniciante",
            "format_generated": "tutorial",
            "key_concepts": ["SQL"],
            "study_time_minutes": 4,
            "prerequisites": ["Banco de dados"]
        },
        "content": {
            "title": "Banco de dados",
            "introduction": "Introdução aos bancos de dados.",
            "steps": [
                {
                    "title": "Apostila de banco de dados",
                    "explanation": "Banco de dados são estruturas organizadas de informação.",
                    "example": "PostgreSQL é um sistema de gestão de bases de dados."
                }
            ]
        }
    }

    pacote_validado = EducationalPackage.model_validate(dados_pacote)

    assert isinstance(pacote_validado, EducationalPackage)
    assert isinstance(pacote_validado.content, TutorialContent)


def test_deve_rejeitar_formato_incompativel():
    dados_pacote = {
        "metadata": {
            "profile_applied": "iniciante",
            "format_generated": "tutorial",
            "key_concepts": ["SQL"],
            "study_time_minutes": 4,
            "prerequisites": ["Banco de dados"]
        },
        "content": {
            "title": "Banco de dados",
            "cards": [
                {
                    "card_id": "card_001",
                    "front": "O que quer dizer SQL?",
                    "back": "Structured Query Language"
                }
            ]
        }
    }

    with pytest.raises(ValidationError):
        EducationalPackage.model_validate(dados_pacote)


def test_deve_validar_pacote_de_quiz():
    dados_pacote = {
        "metadata": {
            "profile_applied": "iniciante",
            "format_generated": "quiz",
            "key_concepts": ["Python"],
            "study_time_minutes": 10,
            "prerequisites": ["Lógica de programação"]
        },
        "content": {
            "title": "Fundamentos de Python",
            "questions": [
                {
                    "question_id": "q_001",
                    "question": "O que é Python?",
                    "options": [
                        {
                            "option_id": "A",
                            "text": "Linguagem de programação"
                        },
                        {
                            "option_id": "B",
                            "text": "Sistema operativo"
                        }
                    ],
                    "correct_option_id": "A",
                    "justification": "Python é uma linguagem de programação."
                }
            ]
        }
    }

    pacote_validado = EducationalPackage.model_validate(dados_pacote)

    assert isinstance(pacote_validado, EducationalPackage)
    assert isinstance(pacote_validado.content, QuizContent)


def test_deve_rejeitar_opcoes_com_ids_duplicados():
    dados_pergunta = {
        "question_id": "q_001",
        "question": "O que é Python?",
        "options": [
            {"option_id": "A", "text": "Python"},
            {"option_id": "A", "text": "Java"}
        ],
        "correct_option_id": "A",
        "justification": "Justificação de teste."
    }

    with pytest.raises(ValidationError):
        QuizQuestion.model_validate(dados_pergunta)


def test_deve_rejeitar_resposta_correta_inexistente():
    dados_pergunta = {
        "question_id": "q_001",
        "question": "O que é Python?",
        "options": [
            {"option_id": "A", "text": "Python"},
            {"option_id": "B", "text": "Java"}
        ],
        "correct_option_id": "C",
        "justification": "Justificação de teste."
    }

    with pytest.raises(ValidationError):
        QuizQuestion.model_validate(dados_pergunta)


def test_deve_rejeitar_perguntas_com_ids_duplicados():
    pergunta = {
        "question_id": "q_001",
        "question": "O que é Python?",
        "options": [
            {"option_id": "A", "text": "Python"},
            {"option_id": "B", "text": "Java"}
        ],
        "correct_option_id": "A",
        "justification": "Python é uma linguagem de programação."
    }

    dados_quiz = {
        "title": "Quiz de programação",
        "questions": [
            pergunta,
            pergunta
        ]
    }

    with pytest.raises(ValidationError):
        QuizContent.model_validate(dados_quiz)


def test_deve_rejeitar_flashcards_com_ids_duplicados():
    dados_flashcards = {
        "title": "Fundamentos de programação",
        "cards": [
            {
                "card_id": "card_001",
                "front": "O que é Python?",
                "back": "Uma linguagem de programação."
            },
            {
                "card_id": "card_001",
                "front": "O que é Java?",
                "back": "Uma linguagem de programação."
            }
        ]
    }

    with pytest.raises(ValidationError):
        FlashcardContent.model_validate(dados_flashcards)


def test_deve_rejeitar_quiz_com_formato_flashcards():
    dados_pacote = {
        "metadata": {
            "profile_applied": "iniciante",
            "format_generated": "flashcards",
            "key_concepts": ["Python"],
            "study_time_minutes": 10,
            "prerequisites": []
        },
        "content": {
            "title": "Quiz de programação",
            "questions": [
                {
                    "question_id": "q_001",
                    "question": "O que é Python?",
                    "options": [
                        {"option_id": "A", "text": "Linguagem de programação"},
                        {"option_id": "B", "text": "Sistema operativo"}
                    ],
                    "correct_option_id": "A",
                    "justification": "Python é uma linguagem de programação."
                }
            ]
        }
    }

    with pytest.raises(ValidationError):
        EducationalPackage.model_validate(dados_pacote)
