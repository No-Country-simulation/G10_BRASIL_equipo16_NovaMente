"""Quiz interativo: uma pergunta por vez, feedback imediato e placar final."""

import streamlit as st

from src import estilos
from src.modelos import QuestaoQuiz


def _estado(prefixo: str) -> dict:
    chave = f"{prefixo}_quiz"
    if chave not in st.session_state:
        st.session_state[chave] = {"indice": 0, "respostas": {}, "finalizado": False}
    return st.session_state[chave]


def _confirmar(prefixo: str, questao_id: str, chave_radio: str) -> None:
    escolha = st.session_state.get(chave_radio)
    if escolha is not None:
        _estado(prefixo)["respostas"][questao_id] = escolha


def _proxima(prefixo: str, total: int) -> None:
    e = _estado(prefixo)
    if e["indice"] + 1 >= total:
        e["finalizado"] = True
    else:
        e["indice"] += 1


def _reiniciar(prefixo: str, questoes: tuple[QuestaoQuiz, ...]) -> None:
    st.session_state[f"{prefixo}_quiz"] = {"indice": 0, "respostas": {}, "finalizado": False}
    for q in questoes:
        st.session_state.pop(f"{prefixo}_radio_{q.id}", None)


def _placar(questoes: tuple[QuestaoQuiz, ...], respostas: dict) -> int:
    return sum(1 for q in questoes if respostas.get(q.id) == q.id_correta)


def _render_resultado(questoes: tuple[QuestaoQuiz, ...], prefixo: str) -> None:
    e = _estado(prefixo)
    acertos = _placar(questoes, e["respostas"])
    st.html(estilos.placar_html(acertos, len(questoes)))
    if acertos == len(questoes):
        st.balloons()

    st.markdown("##### Revisão das respostas")
    for i, q in enumerate(questoes, start=1):
        escolhida = e["respostas"].get(q.id)
        certo = escolhida == q.id_correta
        with st.expander(f"{i}. {q.pergunta}", expanded=not certo,
                         icon=":material/check_circle:" if certo else ":material/cancel:"):
            if not certo:
                texto_escolhida = next((o.texto for o in q.opcoes if o.id == escolhida), "—")
                st.markdown(f"Você marcou: *{texto_escolhida}*")
            st.markdown(f"Resposta certa: **{q.resposta_correta.texto}**")
            st.caption(q.justificativa)

    st.button("Refazer o quiz", key=f"{prefixo}_refazer", on_click=_reiniciar, args=(prefixo, questoes))


def renderizar(questoes: tuple[QuestaoQuiz, ...], prefixo: str) -> None:
    total = len(questoes)
    e = _estado(prefixo)
    if e["finalizado"]:
        _render_resultado(questoes, prefixo)
        return

    i = e["indice"]
    questao = questoes[i]
    chave_radio = f"{prefixo}_radio_{questao.id}"
    respondida = questao.id in e["respostas"]

    st.progress((i + (1 if respondida else 0)) / total, text=f"Pergunta {i + 1} de {total}")

    with st.container(border=True):
        st.html(f'<div class="nm-pergunta">{estilos._esc(questao.pergunta)}</div>')
        opcoes = {o.id: o.texto for o in questao.opcoes}
        st.radio(
            "Alternativas",
            options=list(opcoes),
            format_func=lambda oid, opcoes=opcoes: opcoes[oid],
            key=chave_radio,
            index=None if not respondida else list(opcoes).index(e["respostas"][questao.id]),
            disabled=respondida,
            label_visibility="collapsed",
        )

        if not respondida:
            st.button(
                "Confirmar resposta",
                key=f"{prefixo}_conf_{questao.id}",
                type="primary",
                disabled=st.session_state.get(chave_radio) is None,
                on_click=_confirmar,
                args=(prefixo, questao.id, chave_radio),
            )
        else:
            correto = e["respostas"][questao.id] == questao.id_correta
            titulo = "Correto!" if correto else f"Não é essa. Resposta certa: {questao.resposta_correta.texto}"
            st.html(estilos.feedback_html(correto, titulo, questao.justificativa))
            st.button(
                "Ver resultado" if i + 1 == total else "Próxima pergunta →",
                key=f"{prefixo}_prox_{questao.id}",
                type="primary",
                on_click=_proxima,
                args=(prefixo, total),
            )
