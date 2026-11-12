"""Baralho de flashcards: um cartão por vez, com virar / anterior / próximo."""

import streamlit as st

from src import estilos
from src.modelos import Flashcard


def _estado(prefixo: str) -> dict:
    chave = f"{prefixo}_deck"
    if chave not in st.session_state:
        st.session_state[chave] = {"indice": 0, "verso": False, "vistos": set()}
    return st.session_state[chave]


def _virar(prefixo: str) -> None:
    e = _estado(prefixo)
    e["verso"] = not e["verso"]
    e["vistos"].add(e["indice"])


def _mover(prefixo: str, passo: int, total: int) -> None:
    e = _estado(prefixo)
    e["indice"] = (e["indice"] + passo) % total
    e["verso"] = False


def _ir_para(prefixo: str, indice: int) -> None:
    e = _estado(prefixo)
    e["indice"], e["verso"] = indice, False


def renderizar(cartoes: tuple[Flashcard, ...], prefixo: str) -> None:
    total = len(cartoes)
    e = _estado(prefixo)
    cartao = cartoes[e["indice"]]
    lado = "verso" if e["verso"] else "frente"

    st.html(
        estilos.flashcard_html(
            cartao.verso if e["verso"] else cartao.frente,
            lado,
            e["indice"] + 1,
            total,
            dica=None if e["verso"] else "Pense na resposta antes de virar.",
        )
    )

    c_ant, c_virar, c_prox = st.columns([1, 2, 1])
    c_ant.button("← Anterior", key=f"{prefixo}_ant", use_container_width=True,
                 on_click=_mover, args=(prefixo, -1, total))
    c_virar.button("Ver resposta" if not e["verso"] else "Ver pergunta", key=f"{prefixo}_virar",
                   type="primary", use_container_width=True, on_click=_virar, args=(prefixo,))
    c_prox.button("Próximo →", key=f"{prefixo}_prox", use_container_width=True,
                  on_click=_mover, args=(prefixo, 1, total))

    st.progress(len(e["vistos"]) / total, text=f"{len(e['vistos'])} de {total} cartões revelados")

    with st.expander("Ver todos os cartões"):
        for i, c in enumerate(cartoes):
            col_txt, col_btn = st.columns([5, 1])
            col_txt.markdown(f"**{i + 1}. {c.frente}**  \n{c.verso}")
            col_btn.button("Abrir", key=f"{prefixo}_ir_{i}", on_click=_ir_para, args=(prefixo, i))
