import re

import streamlit as st

from src import exportadores
from src.modelos import Requisicao, ResultadoIA


def _slug(texto: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")[:40] or "conteudo"


def renderizar(resultado: ResultadoIA, requisicao: Requisicao) -> None:
    if resultado.pacote is None:
        st.caption("Nada para exportar.")
        return
    base = f"novamente-{_slug(resultado.pacote.titulo)}-{requisicao.perfil}-{requisicao.formato}"
    json_enunciado = exportadores.para_json_enunciado(resultado, requisicao)

    opcoes = {
        "JSON": ("Formato de integração definido no enunciado.", exportadores.para_json_texto(json_enunciado),
                 f"{base}.json", "application/json"),
        "Markdown": ("Para ler, imprimir ou colar em um wiki.", exportadores.para_markdown(resultado),
                     f"{base}.md", "text/markdown"),
        "Anki": ("Duas colunas (frente/verso) separadas por tabulação. No Anki: Arquivo → Importar.",
                 exportadores.para_csv_anki(resultado), f"{base}-anki.txt", "text/plain"),
    }
    colunas = st.columns(len(opcoes))
    for col, (nome, (descricao, dados, nome_arquivo, mime)) in zip(colunas, opcoes.items()):
        with col, st.container(border=True):
            st.markdown(f"**{nome}**")
            st.caption(descricao)
            st.download_button("Baixar", data=dados, file_name=nome_arquivo, mime=mime,
                               key=f"dl_{nome}", use_container_width=True)
