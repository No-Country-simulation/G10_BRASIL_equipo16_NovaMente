import streamlit as st

from src import estilos
from src.modelos import Pacote, Revisao

ROTULO_PERFIL = {"iniciante": "Iniciante", "intermediario": "Intermediário"}
ROTULO_FORMATO = {"flashcards": "Flashcards", "quiz": "Quiz", "tutorial": "Tutorial"}


def _pill_revisao(revisao: Revisao | None) -> str:
    if revisao is None:
        return estilos.pill("sem revisão automática", "cinza")
    if revisao.aprovado:
        return estilos.pill("aprovado pelo revisor", "verde")
    return estilos.pill("revisor pediu correções", "ambar")


def renderizar(pacote: Pacote, revisao: Revisao | None) -> None:
    m = pacote.metadados
    st.markdown(f"## {pacote.titulo}")
    st.html(
        estilos.pill(ROTULO_PERFIL.get(m.perfil, m.perfil))
        + estilos.pill(ROTULO_FORMATO.get(m.formato, m.formato))
        + estilos.pill(f"{m.tempo_estudo_minutos} min de estudo", "cinza")
        + _pill_revisao(revisao)
    )
    if pacote.introducao:
        st.markdown(pacote.introducao)

    if m.conceitos_chave or m.pre_requisitos:
        with st.expander("Conceitos-chave e pré-requisitos", expanded=False):
            if m.conceitos_chave:
                st.html("<div><strong>Conceitos:</strong><br>" + estilos.pills(list(m.conceitos_chave)) + "</div>")
            if m.pre_requisitos:
                st.markdown("**Pré-requisitos:** " + ", ".join(m.pre_requisitos))
