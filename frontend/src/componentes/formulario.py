"""Sidebar: documento, tema, perfil, formato e botão de gerar."""

from dataclasses import dataclass
from pathlib import Path

import streamlit as st

from src.config import CENARIOS_DEMO, EXTENSOES_SUPORTADAS, FORMATOS, MAX_UPLOAD_MB, PERFIS
from src.modelos import Requisicao


@dataclass(frozen=True)
class Envio:
    requisicao: Requisicao
    arquivo_nome: str | None
    arquivo_bytes: bytes | None


def aplicar_cenario(cenario: dict) -> None:
    """Preenche o formulário com um cenário de demo e agenda a geração."""
    st.session_state["campo_pergunta"] = cenario["pergunta"]
    st.session_state["campo_perfil"] = cenario["perfil"]
    st.session_state["campo_formato"] = cenario["formato"]
    st.session_state["cenario_pendente"] = True


def _secao(titulo: str) -> None:
    st.html(f'<div class="nm-secao">{titulo}</div>')


def renderizar(nome_servico: str) -> Envio | None:
    st.session_state.setdefault("campo_perfil", next(iter(PERFIS)))
    st.session_state.setdefault("campo_formato", next(iter(FORMATOS)))
    with st.sidebar:
        _secao("Documento")
        arquivo = st.file_uploader(
            "Documento",
            type=[ext.lstrip(".") for ext in EXTENSOES_SUPORTADAS],
            label_visibility="collapsed",
            help=f"PDF, Markdown ou TXT até {MAX_UPLOAD_MB} MB. Sem upload, usa a base de exemplo (guia de Power BI).",
        )
        if arquivo is None:
            st.caption("Sem arquivo: usa a base de exemplo (Power BI).")

        _secao("Tema")
        st.text_input(
            "Tema",
            key="campo_pergunta",
            placeholder="ex.: O que é o Power Query?",
            label_visibility="collapsed",
        )

        _secao("Perfil")
        st.segmented_control("Perfil", list(PERFIS), key="campo_perfil", label_visibility="collapsed")

        _secao("Formato")
        st.segmented_control("Formato", list(FORMATOS), key="campo_formato", label_visibility="collapsed")

        pergunta = (st.session_state.get("campo_pergunta") or "").strip()
        perfil = st.session_state.get("campo_perfil")
        formato = st.session_state.get("campo_formato")
        pronto = bool(pergunta and perfil and formato)

        st.write("")
        gerar = st.button("Gerar material", type="primary", use_container_width=True, disabled=not pronto)
        if not pronto:
            faltas = [n for n, v in (("tema", pergunta), ("perfil", perfil), ("formato", formato)) if not v]
            st.caption("Falta: " + ", ".join(faltas) + ".")

        st.write("")
        with st.expander("Cenários de demonstração"):
            st.caption("Mesmo documento, perfis e formatos diferentes.")
            for i, cenario in enumerate(CENARIOS_DEMO):
                st.button(cenario["nome"], key=f"cenario_{i}", use_container_width=True,
                          on_click=aplicar_cenario, args=(cenario,))

        st.caption(f"Motor: {nome_servico}")

    disparar = gerar or st.session_state.pop("cenario_pendente", False)
    if not disparar:
        return None

    arquivo_bytes = arquivo.getvalue() if arquivo is not None else None
    if arquivo_bytes is not None and len(arquivo_bytes) > MAX_UPLOAD_MB * 1024 * 1024:
        st.sidebar.error(f"Arquivo maior que {MAX_UPLOAD_MB} MB.")
        return None

    requisicao = Requisicao(
        pergunta=pergunta,
        perfil=PERFIS[st.session_state["campo_perfil"]],
        formato=FORMATOS[st.session_state["campo_formato"]],
        nome_arquivo=arquivo.name if arquivo else None,
        titulo_documento=Path(arquivo.name).stem if arquivo else None,
    )
    return Envio(requisicao=requisicao, arquivo_nome=requisicao.nome_arquivo, arquivo_bytes=arquivo_bytes)
