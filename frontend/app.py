"""NovaMente — interface Streamlit.

Rodar a partir da RAIZ do repositório (os caminhos da ai_stack são relativos a ela):
    streamlit run frontend/app.py
"""

import json
import os

import streamlit as st

from src import config, estilos, exportadores
from src.adaptador import RespostaInvalidaError, adaptar_resposta
from src.componentes import exportar, flashcards, formulario, metadados, qualidade, quiz, tutorial
from src.config import CENARIOS_DEMO
from src.modelos import Flashcard, PassoTutorial, QuestaoQuiz, Requisicao, ResultadoIA
from src.servico import ErroServico, ServicoConteudo

# A ai_stack usa caminhos relativos (./data/chroma_db, docs/rag/...): garantir que o
# processo esteja na raiz do repo, independentemente de onde o streamlit foi chamado.
os.chdir(config.RAIZ_REPO)

st.set_page_config(page_title="NovaMente", page_icon=str(estilos.LOGO_PATH), layout="wide")
estilos.aplicar()


@st.cache_resource(show_spinner=False)
def obter_servico(modo: str) -> ServicoConteudo:
    """Um serviço por processo: no modo IA isso mantém o modelo de embeddings carregado."""
    if modo == "ia":
        from src.servico_ia import ServicoIA

        return ServicoIA()
    from src.servico_mock import ServicoMock

    return ServicoMock()


def executar(servico: ServicoConteudo, envio: formulario.Envio) -> ResultadoIA:
    if envio.arquivo_bytes is not None and envio.arquivo_nome:
        with st.spinner(f"Lendo e indexando {envio.arquivo_nome}…", show_time=True):
            servico.indexar(envio.arquivo_nome, envio.arquivo_bytes)
    with st.spinner("Buscando os trechos relevantes e gerando o material…", show_time=True):
        resposta = servico.gerar(envio.requisicao.pergunta, envio.requisicao.perfil, envio.requisicao.formato)
    return adaptar_resposta(resposta)


def mostrar_conteudo(resultado: ResultadoIA, prefixo: str) -> None:
    itens = resultado.pacote.itens  # type: ignore[union-attr]
    if isinstance(itens[0], Flashcard):
        flashcards.renderizar(itens, prefixo)  # type: ignore[arg-type]
    elif isinstance(itens[0], QuestaoQuiz):
        quiz.renderizar(itens, prefixo)  # type: ignore[arg-type]
    elif isinstance(itens[0], PassoTutorial):
        tutorial.renderizar(itens)  # type: ignore[arg-type]


def mostrar_resultado(resultado: ResultadoIA, requisicao: Requisicao, prefixo: str) -> None:
    if resultado.status == "insufficient_context":
        st.warning("Não encontrei esse tema no documento. Reformule a pergunta ou confira se o arquivo "
                   "trata do assunto.", icon=":material/search_off:")
        return
    if resultado.status == "requires_manual_review":
        st.warning(resultado.mensagem or "O conteúdo não foi aprovado pelo revisor automático.",
                   icon=":material/rate_review:")
        qualidade.renderizar(resultado)
        return

    metadados.renderizar(resultado.pacote, resultado.revisao)  # type: ignore[arg-type]
    aba_conteudo, aba_qualidade, aba_exportar, aba_json = st.tabs(["Estudar", "Qualidade e fontes", "Exportar", "JSON"])
    with aba_conteudo:
        mostrar_conteudo(resultado, prefixo)
    with aba_qualidade:
        qualidade.renderizar(resultado)
    with aba_exportar:
        exportar.renderizar(resultado, requisicao)
    with aba_json:
        st.caption("JSON no formato do enunciado (o mesmo do botão de download):")
        st.code(json.dumps(exportadores.para_json_enunciado(resultado, requisicao), ensure_ascii=False, indent=2),
                language="json")
        with st.expander("Resposta bruta da ai_stack"):
            st.json(resultado.resposta_bruta, expanded=False)


def mostrar_vazio() -> None:
    st.html(estilos.vazio_html())
    st.write("")
    st.markdown("**Ou experimente um cenário pronto** — o mesmo guia de Power BI adaptado de três jeitos:")
    colunas = st.columns(len(CENARIOS_DEMO))
    for col, cenario in zip(colunas, CENARIOS_DEMO):
        with col, st.container(border=True):
            st.markdown(f"**{cenario['nome']}**")
            st.caption(cenario["pergunta"])
            st.button("Gerar", key=f"vazio_{cenario['nome']}", use_container_width=True,
                      on_click=formulario.aplicar_cenario, args=(cenario,))


def cabecalho() -> None:
    modo = estilos.pill("modo demonstração", "ambar") if config.MODO != "ia" else estilos.pill("IA ativa", "verde")
    st.html(f'<div class="nm-hero">{estilos.logo_html()}<h1>NovaMente</h1>{modo}</div>'
            '<p class="nm-sub">Documentação técnica → flashcards, quiz e tutoriais no nível de quem vai estudar.</p>')


def main() -> None:
    cabecalho()
    servico = obter_servico(config.MODO)
    envio = formulario.renderizar(servico.nome)

    if envio is not None:
        try:
            resultado = executar(servico, envio)
        except ErroServico as e:
            st.error(str(e), icon=":material/error:")
        except RespostaInvalidaError as e:
            st.error(f"A IA respondeu em um formato inesperado: {e}", icon=":material/error:")
        else:
            st.session_state["resultado"] = resultado
            st.session_state["requisicao"] = envio.requisicao
            st.session_state["execucao"] = st.session_state.get("execucao", 0) + 1

    resultado = st.session_state.get("resultado")
    if resultado is None:
        mostrar_vazio()
        return

    # prefixo por execução: zera o estado de cartões/quiz a cada geração nova
    mostrar_resultado(resultado, st.session_state["requisicao"], prefixo=f"exec{st.session_state['execucao']}")


if __name__ == "__main__":
    main()
