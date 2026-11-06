
import json

from langchain_core.messages import convert_to_openai_messages

from ai_stack.agents.reviewer_prompts import reviewer_prompt
from ai_stack.llm import gerar_resposta_llm
from ai_stack.schemas import ReviewReport


def revisar_conteudo_educativo(contexto: str, pacote_educativo: dict, perfil: str,formato_educativo: str) -> ReviewReport:

    pacote_educativo_json = json.dumps(
        pacote_educativo,
        ensure_ascii=False,
        indent=2
    )

    valor_prompt = reviewer_prompt.invoke({
        "context": contexto,
        "educational_package": pacote_educativo_json,
        "profile": perfil,
        "format": formato_educativo
    })

    mensagens_langchain = valor_prompt.to_messages()

    mensagens = convert_to_openai_messages(mensagens_langchain)

    resposta = gerar_resposta_llm(mensagens)

    if not resposta or not resposta.strip():
        raise ValueError("O Revisor devolveu uma resposta vazia.")

    try:
        dados_resposta = json.loads(resposta)

    except json.JSONDecodeError as erro:
        raise ValueError(
            f"O Revisor devolveu JSON inválido: {erro}"
        ) from erro

    relatorio_revisao = ReviewReport.model_validate(dados_resposta)

    return relatorio_revisao
