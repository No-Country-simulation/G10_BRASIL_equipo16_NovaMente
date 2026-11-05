
import json

from langchain_core.messages import convert_to_openai_messages
from ai_stack.agents.reviewer import revisar_conteudo_educativo
from ai_stack.retrieval import recuperar_documentos_relevantes
from ai_stack.llm import  gerar_resposta_llm
from ai_stack.schemas import Formats,EducationalPackage,ReviewReport, ReviewStatus
from ai_stack.generator_prompts import generation_prompt, correction_prompt

MAX_RODADAS_CORRECAO = 2
def validar_nivel(nivel):
        if not isinstance(nivel,str) :
            nivel="iniciante"

        nivel = nivel.strip().lower()

        if nivel not in ["iniciante","intermediario"]:
                 nivel="iniciante"

        return nivel

def validar_formato(formato):
    if not isinstance(formato,str):
            raise TypeError("Tipo invalido")

    formato= formato.strip().lower()

    formato_convertido= Formats(formato)
    return formato_convertido
def gerar_conteudo_corrigido( contexto: str, pacote_educativo: dict, relatorio_revisao: ReviewReport,perfil: str,formato: str) -> dict:
    if relatorio_revisao.status != ReviewStatus.correction_required:
      raise ValueError(
        "O conteúdo não necessita de correção."
    )

    pacote_educativo_json = json.dumps(
        pacote_educativo,
        ensure_ascii=False,
        indent=2
    )

    relatorio_revisao_json = json.dumps(
        relatorio_revisao.model_dump(mode="json"),
        ensure_ascii=False,
        indent=2
    )

    valor_prompt_correcao = correction_prompt.invoke({
        "context": contexto,
    "educational_package": pacote_educativo_json,
    "review_report": relatorio_revisao_json,
    "profile": perfil,
    "format": formato
    })

    mensagens = convert_to_openai_messages(
        valor_prompt_correcao.to_messages()
    )

    resposta_corrigida =  gerar_resposta_llm(mensagens)

    if not resposta_corrigida or not resposta_corrigida.strip():
        raise ValueError("O Corrector devolveu uma resposta vazia.")

    try:
        dados_resposta = json.loads(resposta_corrigida)

    except json.JSONDecodeError as erro:
        raise ValueError(
            f"O LLM devolveu JSON inválido: {erro}"
        ) from erro
    if not isinstance(dados_resposta, dict):
        raise TypeError(
            "A resposta do LLM deveria ser um objeto JSON, "
            f"mas foi recebido: {type(dados_resposta).__name__}"
        )

    pacote_validado = EducationalPackage.model_validate(dados_resposta)

    return pacote_validado.model_dump(mode="json")

def gerar_resposta_rag( pergunta: str, banco_vetorial, nivel: str,formato: str) -> dict:
    # 1. Validar os parâmetros de entrada
    nivel_validado = validar_nivel(nivel)
    formato_validado = validar_formato(formato)

    # 2. Recuperar documentos relevantes
    documentos_fonte = recuperar_documentos_relevantes(banco_vetorial, pergunta, quantidade_documentos=3)

    if not documentos_fonte:
        return {
            "status": "insufficient_context",
            "answer": None,
            "sources": [],
            "message": "Não foram encontrados documentos relevantes."
        }

    # 3. Construir o contexto e os metadados das fontes
    contexto = "\n\n".join(
        [
            (
                f"Fonte: {documento.metadata.get('source', 'Desconhecido')}\n"
                f"Contexto: {documento.page_content}\n"
                f"Página: {documento.metadata.get('page', 'Desconhecido')}"
            )
            for documento in documentos_fonte
        ]
    )

    metadados_fontes = [
        {
            "source": documento.metadata.get("source", "Desconhecido"),
            "page": documento.metadata.get("page", "Desconhecido")
        }
        for documento in documentos_fonte
    ]

    # 4. Gerar o conteúdo educativo
    valor_prompt_geracao = generation_prompt.invoke({
        "context": contexto,
        "question": pergunta,
        "level": nivel_validado,
        "format": formato_validado.value
    })

    mensagens = convert_to_openai_messages(
        valor_prompt_geracao.to_messages()
    )

    resposta_bruta =  gerar_resposta_llm(mensagens)

    if not isinstance(resposta_bruta, str) or not resposta_bruta.strip():
        raise ValueError("O LLM devolveu uma resposta vazia ou inválida.")

    try:
        dados_resposta = json.loads(resposta_bruta)

    except json.JSONDecodeError as erro:
        raise ValueError(
            f"O LLM devolveu JSON inválido: {erro}"
        ) from erro

    pacote_validado = EducationalPackage.model_validate(dados_resposta)

    pacote_educativo = pacote_validado.model_dump(mode="json")

    # 5. Inicializar o estado da revisão
    relatorio_revisao = None
    rodadas_correcao = 0

    # 6. Executar o ciclo de revisão e correção
    if formato_validado in (Formats.quiz, Formats.flashcards):

        relatorio_revisao = revisar_conteudo_educativo(
            contexto=contexto,
            pacote_educativo=pacote_educativo,
            perfil=nivel_validado,
            formato_educativo=formato_validado.value
        )

        while (
            relatorio_revisao.status == ReviewStatus.correction_required
            and rodadas_correcao < MAX_RODADAS_CORRECAO
        ):

            # Corrigir a versão actual do pacote educativo
            pacote_educativo = gerar_conteudo_corrigido(
                contexto=contexto,
                pacote_educativo=pacote_educativo,
                relatorio_revisao=relatorio_revisao,
                perfil=nivel_validado,
                formato=formato_validado.value
            )

            rodadas_correcao += 1

            # Avaliar novamente o conteúdo corrigido
            relatorio_revisao = revisar_conteudo_educativo(
                contexto =contexto,
                pacote_educativo=pacote_educativo,
                perfil=nivel_validado,
                formato_educativo=formato_validado.value
            )

    # 7. Impedir a entrega de conteúdo que não foi aprovado
    if (
        relatorio_revisao is not None
        and relatorio_revisao.status == ReviewStatus.correction_required
    ):
        return {
            "status": "requires_manual_review",
            "answer": None,
            "sources": metadados_fontes,
            "message": (
                f"O conteúdo não foi aprovado após "
                f"{rodadas_correcao} rondas de correção. "
                "É necessária uma revisão manual."
            ),
            "review_report": relatorio_revisao.model_dump(mode="json")
        }

    # 8. Preparar o relatório final
    dados_relatorio_revisao = (
        relatorio_revisao.model_dump(mode="json")
        if relatorio_revisao is not None
        else None
    )

    # 9. Devolver o resultado
    return {
        "status": "success",
        "answer": pacote_educativo,
        "sources": metadados_fontes,
        "message": None,
        "review_report": dados_relatorio_revisao
    }