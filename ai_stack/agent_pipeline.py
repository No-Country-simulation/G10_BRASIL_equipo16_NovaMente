import os
from typing import List, Literal, TypedDict

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field

# Carrega variáveis de ambiente (GOOGLE_API_KEY)
load_dotenv()


# ==========================================
# 1. DEFINIÇÃO DO SCHEMA DE SAÍDA (JSON)
# ==========================================
class ConteudoEducacional(BaseModel):
    titulo: str = Field(description="Título atrativo e adequado ao perfil escolhido.")
    perfil_destinatario: str = Field(
        description="Perfil para o qual o conteúdo foi adaptado."
    )
    nicho_aplicacao: str = Field(description="Indústria ou contexto de aplicação.")
    formato_pedagogico: str = Field(
        description="Formato escolhido (Tutorial, Quiz, Flashcards, Resumo, etc.)."
    )
    tempo_estimado_minutos: int = Field(
        description="Tempo estimado de estudo em minutos."
    )
    pre_requisitos: List[str] = Field(
        description="Conhecimentos prévios necessários para compreender o material."
    )
    conceitos_chave: List[str] = Field(
        description="Lista dos principais termos técnicos e conceitos abordados."
    )
    conteudo_estruturado: str = Field(
        description="O conteúdo educacional completo em Markdown, adaptado ao formato e perfil."
    )
    score_fidelidade: int = Field(
        description="Nota de 1 a 10 indicando o quanto o texto se manteve fiel ao material original sem alucinações."
    )
    observacoes_revisao: str = Field(
        description="Notas do agente revisor sobre a precisão técnica em relação à fonte."
    )


# ==========================================
# 2. ESTADO DO GRAFO DE AGENTES (LANGGRAPH)
# ==========================================
class AgentState(TypedDict):
    contexto_rag: str
    perfil: str
    formato: str
    nicho: str
    rascunho_gerado: str
    resultado_final: dict


# ==========================================
# 3. INICIALIZAÇÃO DO MODELO GEMINI
# ==========================================
# Usando gemini-2.5-flash por ser rápido, gratuito na camada free e excelente com JSON estruturado
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,  # Temperatura baixa para reduzir criatividade excessiva e evitar alucinações
)


# ==========================================
# 4. NÓS DO GRAFO (AGENTES)
# ==========================================
def agente_redator(state: AgentState):
    """Gera a primeira versão do conteúdo pedagógico baseado estritamente no contexto RAG."""
    print("✍️ [Agente Redator] Elaborando material didático personalizado...")

    prompt_redator = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Você é um Designer Instrucional e Arquiteto de Conteúdo Técnico de elite.
Sua missão é transformar documentações técnicas densas em materiais educacionais altamente eficazes.

REGRAS ESTRITAS:
1. Baseie-se EXCLUSIVAMENTE nos trechos da documentação fornecidos no contexto abaixo.
2. NÃO invente funcionalidades, comandos, bibliotecas ou regras que não estejam no texto original.
3. Adapte o vocabulário, a profundidade e os exemplos para:
   - Perfil do Destinatário: {perfil}
   - Formato Pedagógico: {formato}
   - Nicho / Contexto de Aplicação: {nicho}
4. Se o formato for 'Quiz Interativo', inclua perguntas, alternativas e justificativas detalhadas baseadas no texto.
5. Se o formato for 'Flashcards', estruture pares claros de Pergunta/Conceito -> Resposta/Explicação.""",
            ),
            (
                "human",
                """Contexto Técnico Extraído (RAG):
---
{contexto_rag}
---
Gere agora o conteúdo educacional completo e inclua sugestões de conceitos-chave, pré-requisitos e tempo estimado de estudo.""",
            ),
        ]
    )

    chain = prompt_redator | llm
    resposta = chain.invoke(
        {
            "perfil": state["perfil"],
            "formato": state["formato"],
            "nicho": state["nicho"],
            "contexto_rag": state["contexto_rag"],
        }
    )

    return {"rascunho_gerado": resposta.content}


def agente_revisor_fidelidade(state: AgentState):
    """Audita o rascunho contra o contexto original e formata a saída final em JSON estruturado."""
    print("🕵️ [Agente Revisor] Validando fidelidade técnica e estruturando JSON...")

    # Força o Gemini a responder rigorosamente no formato do Pydantic Schema
    llm_estruturado = llm.with_structured_output(ConteudoEducacional)

    prompt_revisor = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Você é um Auditor Técnico de Qualidade Pedagógica.
Sua função é comparar o Rascunho Educacional gerado com o Contexto Técnico Original (RAG).

TAREFAS:
1. Verifique se há qualquer alucinação, dado inventado ou contradição em relação ao Contexto Original. Se houver, corrija imediatamente no campo 'conteudo_estruturado'.
2. Avalie se o tom e a profundidade realmente atendem ao perfil '{perfil}' no contexto de '{nicho}' e no formato '{formato}'.
3. Atribua um 'score_fidelidade' de 1 a 10 e preencha todos os metadados estruturados solicitados.""",
            ),
            (
                "human",
                """CONTEXTO TÉCNICO ORIGINAL:
---
{contexto_rag}
---

RASCUNHO EDUCACIONAL GERADO:
---
{rascunho_gerado}
---

Produza o objeto final validado e estruturado.""",
            ),
        ]
    )

    chain = prompt_revisor | llm_estruturado
    resultado_validado: ConteudoEducacional = chain.invoke(
        {
            "perfil": state["perfil"],
            "formato": state["formato"],
            "nicho": state["nicho"],
            "contexto_rag": state["contexto_rag"],
            "rascunho_gerado": state["rascunho_gerado"],
        }
    )

    return {"resultado_final": resultado_validado.model_dump()}


# ==========================================
# 5. CONSTRUÇÃO E COMPILAÇÃO DO WORKFLOW
# ==========================================
def criar_grafo_agentes():
    workflow = StateGraph(AgentState)

    # Adiciona os nós
    workflow.add_node("redator", agente_redator)
    workflow.add_node("revisor", agente_revisor_fidelidade)

    # Define o fluxo linear de execução
    workflow.set_entry_point("redator")
    workflow.add_edge("redator", "revisor")
    workflow.add_edge("revisor", END)

    return workflow.compile()


def gerar_material_educacional(
    contexto_rag: str, perfil: str, formato: str, nicho: str
) -> dict:
    """Função principal para ser chamada pelo backend ou interface."""
    app = criar_grafo_agentes()

    estado_inicial = {
        "contexto_rag": contexto_rag,
        "perfil": perfil,
        "formato": formato,
        "nicho": nicho,
        "rascunho_gerado": "",
        "resultado_final": {},
    }

    resultado = app.invoke(estado_inicial)
    return resultado["resultado_final"]


# ==========================================
# TESTE LOCAL ISOLADO
# ==========================================
if __name__ == "__main__":
    import json

    contexto_simulado = """
    Para autenticar requisições na API v2 de Pagamentos Instantâneos, o cliente deve enviar 
    um cabeçalho 'Authorization: Bearer <TOKEN_JWT>'. O token expira em 300 segundos e deve 
    ser renovado através do endpoint POST /oauth/token utilizando client_id e client_secret 
    codificados em Base64. Requisições sem token retornam HTTP 401 Unauthorized.
    """

    saida = gerar_material_educacional(
        contexto_rag=contexto_simulado,
        perfil="Iniciante / Transição de Carreira",
        formato="Guia Prático Passo a Passo (Tutorial)",
        nicho="Fintech",
    )

    print("\n✅ JSON FINAL VALIDADO:")
    print(json.dumps(saida, indent=2, ensure_ascii=False))
