import streamlit as st

from src import estilos
from src.modelos import PassoTutorial


def renderizar(passos: tuple[PassoTutorial, ...]) -> None:
    st.html("".join(
        estilos.passo_html(i, p.titulo, p.explicacao, p.exemplo) for i, p in enumerate(passos, start=1)
    ))
