import os

from dotenv import load_dotenv
from groq import Groq

from ai_stack.config import LLM_MODEL


# Carregar variáveis de ambiente
load_dotenv()

CHAVE_API_GROQ = os.getenv("GROQ_API_KEY")

if not CHAVE_API_GROQ:
    raise RuntimeError(
        "A variável de ambiente GROQ_API_KEY não está definida."
    )


# Inicializar cliente da Groq
cliente_groq = Groq(api_key=CHAVE_API_GROQ)


def gerar_resposta_llm(mensagens):
    """
    Envia mensagens ao modelo de linguagem e devolve a resposta.

    A resposta é solicitada no formato JSON.
    """

    resposta_modelo = cliente_groq.chat.completions.create(
        model=LLM_MODEL,
        messages=mensagens,
        response_format={"type": "json_object"}
    )

    return resposta_modelo.choices[0].message.content