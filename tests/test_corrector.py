from unittest.mock import Mock

import pytest
from pydantic import ValidationError

import ai_stack.rag_pipeline as pipeline
from ai_stack.schemas import (
    EducationalPackage,
    ReviewCategory,
    ReviewIssue,
    ReviewReport,
    ReviewStatus,
)



# FUNÇÕES AUXILIARES


def criar_pacote_educativo_com_erro():
    """
    Cria um pacote educativo com uma resposta incorreta
    para permitir testar o processo de correção.
    """

    return EducationalPackage.model_validate({
        "metadata": {
            "profile_applied": "intermediario",
            "format_generated": "quiz",
            "key_concepts": ["Query Folding", "Power Query"],
            "study_time_minutes": 10,
            "prerequisites": [],
        },
        "content": {
            "title": "Quiz sobre Query Folding (Com Erro Propositado)",
            "questions": [
                {
                    "question_id": "q_001",
                    "question": "O que caracteriza o Query Folding?",
                    "options": [
                        {
                            "option_id": "A",
                            "text": "A conversão obrigatória de todas as tabelas locais diretamente para ficheiros CSV.",
                        },
                        {
                            "option_id": "B",
                            "text": "A tradução das transformações para a linguagem da fonte de dados.",
                        },
                        {
                            "option_id": "C",
                            "text": "A eliminação automática de todas as transformações aplicadas.",
                        },
                        {
                            "option_id": "D",
                            "text": "A execução local de todo o processamento sem consultar a fonte.",
                        },
                    ],
                    "correct_option_id": "A",
                    "justification": "O Query Folding converte as tabelas em formato CSV para otimizar o espaço.",
                }
            ],
        },
    })


def criar_relatorio_revisao():
    """
    Cria um relatório de revisão que identifica
    um problema de precisão técnica no quiz.
    """

    return ReviewReport(
        status=ReviewStatus.correction_required,
        summary="Foi identificada uma definição tecnicamente incorreta.",
        issues=[
            ReviewIssue(
                item_id="q_001",
                item_type="question",
                category=ReviewCategory.technical_accuracy,
                description="A definição de Query Folding está incorreta.",
                evidence="O contexto explica que as transformações são traduzidas para a linguagem da fonte de dados.",
                suggestion="Corrigir o enunciado e a resposta da pergunta.",
            )
        ],
    )


def criar_resposta_json_corrigida():
    """
    Devolve uma resposta JSON válida com o conteúdo corrigido.
    """

    return """
    {
        "metadata": {
            "profile_applied": "intermediario",
            "format_generated": "quiz",
            "key_concepts": [
                "Query Folding",
                "Power Query"
            ],
            "study_time_minutes": 10,
            "prerequisites": []
        },
        "content": {
            "title": "Quiz sobre Query Folding",
            "questions": [
                {
                    "question_id": "q_001",
                    "question": "O que caracteriza o Query Folding?",
                    "options": [
                        {
                            "option_id": "A",
                            "text": "A conversão obrigatória de todas as tabelas locais diretamente para ficheiros CSV."
                        },
                        {
                            "option_id": "B",
                            "text": "A tradução das transformações para a linguagem da fonte de dados."
                        },
                        {
                            "option_id": "C",
                            "text": "A eliminação automática de todas as transformações aplicadas."
                        },
                        {
                            "option_id": "D",
                            "text": "A execução local de todo o processamento sem consultar a fonte."
                        }
                    ],
                    "correct_option_id": "B",
                    "justification": "O Query Folding traduz as transformações para a linguagem da fonte de dados, permitindo que esta execute as operações compatíveis."
                }
            ]
        }
    }
    """


def configurar_llm_simulado(monkeypatch, resposta_llm):
    """
    Substitui o LLM real por um Mock que devolve
    a resposta definida pelo teste.
    """

    llm_simulado = Mock(return_value=resposta_llm)

    monkeypatch.setattr(
        pipeline,
        "gerar_resposta_llm",
        llm_simulado,
    )

    return llm_simulado


def executar_correcao(pacote_educativo, relatorio_revisao):
    """
    Executa o processo de correção utilizando
    os parâmetros padrão dos testes.
    """

    return pipeline.gerar_conteudo_corrigido(
        contexto="O que é Query Folding?",
        pacote_educativo=pacote_educativo.model_dump(mode="json"),
        relatorio_revisao=relatorio_revisao,
        perfil="intermediario",
        formato="quiz",
    )



# TESTES DO CORRETOR


def test_corretor_corrige_conteudo_com_sucesso(monkeypatch):

    pacote_educativo = criar_pacote_educativo_com_erro()
    relatorio_revisao = criar_relatorio_revisao()

    configurar_llm_simulado(
        monkeypatch,
        criar_resposta_json_corrigida(),
    )

    pacote_corrigido = executar_correcao(
        pacote_educativo,
        relatorio_revisao,
    )

    assert pacote_corrigido["content"]["questions"][0]["correct_option_id"] == "B"

    assert pacote_corrigido["content"]["questions"][0]["question_id"] == "q_001"


def test_corretor_rejeita_resposta_vazia(monkeypatch):

    pacote_educativo = criar_pacote_educativo_com_erro()
    relatorio_revisao = criar_relatorio_revisao()

    configurar_llm_simulado(
        monkeypatch,
        "",
    )

    with pytest.raises(ValueError, match="resposta vazia"):
        executar_correcao(
            pacote_educativo,
            relatorio_revisao,
        )


def test_corretor_rejeita_json_invalido(monkeypatch):

    pacote_educativo = criar_pacote_educativo_com_erro()
    relatorio_revisao = criar_relatorio_revisao()

    configurar_llm_simulado(
        monkeypatch,
        "Este texto não está em formato JSON válido",
    )

    with pytest.raises(ValueError, match=" JSON inválido"):
        executar_correcao(
            pacote_educativo,
            relatorio_revisao,
        )


def test_corretor_rejeita_estrutura_invalida(monkeypatch):

    pacote_educativo = criar_pacote_educativo_com_erro()
    relatorio_revisao = criar_relatorio_revisao()

    resposta_json_invalida = """
    {
        "title": "Quiz sobre Query Folding"
    }
    """

    configurar_llm_simulado(
        monkeypatch,
        resposta_json_invalida,
    )

    with pytest.raises(ValidationError):
        executar_correcao(
            pacote_educativo,
            relatorio_revisao,
        )


def test_corretor_rejeita_relatorio_aprovado(monkeypatch):

    pacote_educativo = criar_pacote_educativo_com_erro()

    llm_simulado = Mock()

    monkeypatch.setattr(
        pipeline,
        "gerar_resposta_llm",
        llm_simulado,
    )

    relatorio_aprovado = ReviewReport(
        status=ReviewStatus.approved,
        summary="O conteúdo está correto.",
        issues=[],
    )

    with pytest.raises(
        ValueError,
        match="O conteúdo não necessita de correção.",
    ):
        executar_correcao(
            pacote_educativo,
            relatorio_aprovado,
        )

    llm_simulado.assert_not_called()


def test_corretor_chama_llm_apenas_uma_vez(monkeypatch):

    pacote_educativo = criar_pacote_educativo_com_erro()
    relatorio_revisao = criar_relatorio_revisao()

    llm_simulado = configurar_llm_simulado(
        monkeypatch,
        criar_resposta_json_corrigida(),
    )

    executar_correcao(
        pacote_educativo,
        relatorio_revisao,
    )

    llm_simulado.assert_called_once()


def test_corretor_envia_dados_corretos_ao_llm(monkeypatch):

    pacote_educativo = criar_pacote_educativo_com_erro()
    relatorio_revisao = criar_relatorio_revisao()

    llm_simulado = configurar_llm_simulado(
        monkeypatch,
        criar_resposta_json_corrigida(),
    )

    executar_correcao(
        pacote_educativo,
        relatorio_revisao,
    )

    mensagens_enviadas = llm_simulado.call_args.args[0]

    mensagem_usuario = mensagens_enviadas[1]["content"]