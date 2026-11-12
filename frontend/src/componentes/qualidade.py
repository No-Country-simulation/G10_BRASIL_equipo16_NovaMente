"""Transparência: relatório do agente revisor e fontes usadas pelo RAG."""

import streamlit as st

from src.modelos import ResultadoIA

CATEGORIA = {
    "source_fidelity": "Fidelidade à fonte",
    "technical_accuracy": "Precisão técnica",
    "ambiguity": "Ambiguidade",
    "pedagogical_quality": "Qualidade pedagógica",
}


def renderizar(resultado: ResultadoIA) -> None:
    col_rev, col_fontes = st.columns(2)

    with col_rev, st.container(border=True):
        st.markdown("##### Revisão automática")
        revisao = resultado.revisao
        if revisao is None:
            st.caption("Este formato ainda não passa pelo agente revisor.")
        elif revisao.aprovado:
            st.success(revisao.resumo, icon=":material/verified:")
        else:
            st.warning(revisao.resumo, icon=":material/rate_review:")
            for p in revisao.problemas:
                with st.expander(f"{CATEGORIA.get(p.categoria, p.categoria)} · item {p.item_id}"):
                    st.write(p.descricao)
                    st.caption(f"Evidência: {p.evidencia}")
                    st.caption(f"Sugestão: {p.sugestao}")

    with col_fontes, st.container(border=True):
        st.markdown("##### Fontes usadas")
        if not resultado.fontes:
            st.caption("Nenhuma fonte devolvida.")
        else:
            vistas: set[tuple[str, str]] = set()
            for f in resultado.fontes:
                if (f.arquivo, f.pagina) in vistas:
                    continue
                vistas.add((f.arquivo, f.pagina))
                st.markdown(f":material/description: `{f.arquivo}` · pág. {f.pagina}")
            st.caption("O conteúdo foi gerado apenas a partir destes trechos.")
