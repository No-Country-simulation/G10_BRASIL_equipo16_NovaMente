from ai_stack.schemas import (
    EducationalPackage,
    FlashcardContent,
    TutorialContent,
    QuizContent,
    QuizQuestion,
)
from pydantic import ValidationError
import pytest



def test_flashcard():
    dados = {
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

    dados_validados = EducationalPackage.model_validate(dados)

    assert isinstance(dados_validados, EducationalPackage)
    assert isinstance(dados_validados.content, FlashcardContent)


def test_tutorial():
    dados = {
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

    dados_validados = EducationalPackage.model_validate(dados)

    assert isinstance(dados_validados, EducationalPackage)
    assert isinstance(dados_validados.content, TutorialContent)


def test_formato_incompativel():
    dados = {
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
        EducationalPackage.model_validate(dados)

    
def test_quiz_valido():
    dados = {
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

    dados_validados = EducationalPackage.model_validate(dados)

    assert isinstance(dados_validados, EducationalPackage)
    assert isinstance(dados_validados.content, QuizContent)


# 2. Rejeitar opções com identificadores duplicados
def test_quiz_opcoes_duplicadas():
    dados = {
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
        QuizQuestion.model_validate(dados)


# 3. Rejeitar resposta correta inexistente
def test_quiz_resposta_inexistente():
    dados = {
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
        QuizQuestion.model_validate(dados)


# 4. Rejeitar perguntas com identificadores duplicados
def test_quiz_perguntas_duplicadas():
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

    dados = {
        "title": "Quiz de programação",
        "questions": [
            pergunta,
            pergunta
        ]
    }

    with pytest.raises(ValidationError):
        QuizContent.model_validate(dados)


# 5. Rejeitar Flashcards com identificadores duplicados
def test_flashcards_ids_duplicados():
    dados = {
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
        FlashcardContent.model_validate(dados)


# 6. Rejeitar Quiz associado ao formato Flashcards
def test_quiz_formato_incompativel():
    dados = {
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
        EducationalPackage.model_validate(dados)