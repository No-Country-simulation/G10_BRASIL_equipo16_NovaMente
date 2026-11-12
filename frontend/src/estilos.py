"""Identidade visual da interface: CSS global e pequenos blocos HTML reutilizáveis.

Tudo que é visual fica aqui; os componentes só chamam `pill()`, `cartao()` etc.
O texto que entra nos blocos é sempre escapado (html.escape) — nunca confie no conteúdo da LLM.
"""

import base64
import html
from pathlib import Path

import streamlit as st

CSS = """
<style>
:root {
  --nm-roxo: #6C4AB6;
  --nm-roxo-claro: #EFEAFB;
  --nm-tinta: #1F1B2E;
  --nm-cinza: #6B6680;
  --nm-borda: #E6E2F0;
  --nm-verde: #1E8E5A;
  --nm-verde-claro: #E6F6EE;
  --nm-vermelho: #C0392B;
  --nm-vermelho-claro: #FBECEA;
  --nm-ambar-claro: #FFF4DC;
}

/* respiro geral e largura de leitura */
/* a barra do Streamlit (~3.75rem) é fixa e sobrepõe o conteúdo: o topo precisa ficar abaixo dela */
.block-container { padding-top: 4.5rem; max-width: 1100px; }
h1, h2, h3 { letter-spacing: -0.01em; }

/* botões: cantos suaves, sem gritar */
.stButton > button, .stDownloadButton > button { border-radius: 10px; font-weight: 500; }
.stButton > button[kind="primary"] { box-shadow: 0 4px 14px rgba(108, 74, 182, 0.22); }

/* cabeçalho */
.nm-hero { display: flex; align-items: center; gap: .75rem; flex-wrap: wrap; margin-bottom: .25rem; }
.nm-hero h1 { margin: 0; font-size: 2rem; }
.nm-logo { width: 40px; height: 40px; flex: 0 0 auto; filter: drop-shadow(0 3px 8px rgba(90, 59, 163, .25)); }
.nm-sub { color: var(--nm-cinza); margin: 0 0 1.4rem 0; }

/* pílulas / badges */
.nm-pill {
  display: inline-block; padding: .18rem .65rem; border-radius: 999px; font-size: .78rem;
  font-weight: 600; letter-spacing: .01em; margin: 0 .35rem .35rem 0; white-space: nowrap;
}
.nm-pill.roxo { background: var(--nm-roxo-claro); color: var(--nm-roxo); }
.nm-pill.cinza { background: #F1F0F5; color: var(--nm-cinza); }
.nm-pill.verde { background: var(--nm-verde-claro); color: var(--nm-verde); }
.nm-pill.ambar { background: var(--nm-ambar-claro); color: #8A5A00; }
.nm-pill.vermelho { background: var(--nm-vermelho-claro); color: var(--nm-vermelho); }

/* cartão genérico */
.nm-card {
  border: 1px solid var(--nm-borda); border-radius: 16px; padding: 1.1rem 1.3rem;
  background: #fff; box-shadow: 0 1px 2px rgba(31, 27, 46, .04);
}
.nm-card + .nm-card { margin-top: .75rem; }
.nm-card .nm-rotulo { font-size: .72rem; text-transform: uppercase; letter-spacing: .08em; color: var(--nm-cinza); }

/* flashcard (baralho) */
.nm-flash {
  min-height: 230px; border-radius: 20px; padding: 1.6rem 1.8rem; display: flex; flex-direction: column;
  justify-content: center; gap: .6rem; position: relative; transition: background .25s ease;
}
.nm-flash.frente { background: linear-gradient(135deg, #F7F4FD 0%, #EFEAFB 100%); border: 1px solid #DDD4F3; }
.nm-flash.verso  { background: linear-gradient(135deg, #FFFFFF 0%, #F6F5FA 100%); border: 1px solid var(--nm-borda); }
.nm-flash .nm-rotulo { position: absolute; top: 1rem; left: 1.4rem; font-size: .72rem;
  text-transform: uppercase; letter-spacing: .08em; color: var(--nm-cinza); }
.nm-flash .nm-texto { font-size: 1.25rem; line-height: 1.45; color: var(--nm-tinta); }
.nm-flash.frente .nm-texto { font-weight: 600; font-size: 1.4rem; }
.nm-flash .nm-dica { color: var(--nm-cinza); font-size: .85rem; }

/* quiz */
.nm-pergunta { font-size: 1.15rem; font-weight: 600; line-height: 1.4; margin: .2rem 0 .6rem 0; }
.nm-feedback { border-radius: 12px; padding: .8rem 1rem; margin-top: .6rem; }
.nm-feedback.ok { background: var(--nm-verde-claro); border-left: 4px solid var(--nm-verde); }
.nm-feedback.erro { background: var(--nm-vermelho-claro); border-left: 4px solid var(--nm-vermelho); }
.nm-feedback p { margin: .15rem 0; }
.nm-placar { text-align: center; padding: 1.4rem; }
.nm-placar .nm-num { font-size: 3rem; font-weight: 700; color: var(--nm-roxo); line-height: 1; }

/* tutorial (linha do tempo) */
.nm-passo { display: grid; grid-template-columns: 2.2rem 1fr; gap: .9rem; padding: .2rem 0 1.2rem 0; position: relative; }
.nm-passo::before { content: ""; position: absolute; left: 1.05rem; top: 2.3rem; bottom: 0; width: 2px; background: var(--nm-borda); }
.nm-passo:last-child::before { display: none; }
.nm-passo .nm-bola { width: 2.2rem; height: 2.2rem; border-radius: 50%; background: var(--nm-roxo); color: #fff;
  display: flex; align-items: center; justify-content: center; font-weight: 700; z-index: 1; }
.nm-passo h4 { margin: .3rem 0 .3rem 0; }
.nm-passo p { margin: 0; color: var(--nm-tinta); }
.nm-passo pre { margin-top: .6rem; background: #F6F5FA; border: 1px solid var(--nm-borda); border-radius: 10px; padding: .7rem .9rem; font-size: .86rem; overflow-x: auto; }

/* estado vazio */
.nm-vazio { border: 1px dashed #D5CFE8; border-radius: 16px; padding: 1.4rem 1.6rem; background: #FBFAFE; }
.nm-vazio ol { margin: .4rem 0 0 1.1rem; padding: 0; color: var(--nm-tinta); }
.nm-vazio li { margin: .25rem 0; }

/* sidebar */
[data-testid="stSidebar"] .nm-secao { font-size: .72rem; text-transform: uppercase; letter-spacing: .1em;
  color: var(--nm-cinza); font-weight: 700; margin: .4rem 0 .2rem 0; }
</style>
"""


LOGO_PATH = Path(__file__).resolve().parents[1] / "assets" / "logo.svg"


def aplicar() -> None:
    st.html(CSS)


def logo_html() -> str:
    # st.html remove tags <svg> ao sanitizar; como <img> é permitido, embutimos o SVG em data URI.
    svg_b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f'<img class="nm-logo" alt="" src="data:image/svg+xml;base64,{svg_b64}">'


def _esc(texto: str) -> str:
    return html.escape(texto or "")


def pill(texto: str, tom: str = "roxo") -> str:
    return f'<span class="nm-pill {tom}">{_esc(texto)}</span>'


def pills(itens: list[str], tom: str = "cinza") -> str:
    return "".join(pill(i, tom) for i in itens)


def flashcard_html(texto: str, lado: str, numero: int, total: int, dica: str | None = None) -> str:
    rotulo = f"{'frente' if lado == 'frente' else 'verso'} · cartão {numero} de {total}"
    dica_html = f'<div class="nm-dica">{_esc(dica)}</div>' if dica else ""
    return (
        f'<div class="nm-flash {lado}"><div class="nm-rotulo">{rotulo}</div>'
        f'<div class="nm-texto">{_esc(texto)}</div>{dica_html}</div>'
    )


def feedback_html(correto: bool, titulo: str, explicacao: str) -> str:
    classe = "ok" if correto else "erro"
    return (
        f'<div class="nm-feedback {classe}"><p><strong>{_esc(titulo)}</strong></p>'
        f"<p>{_esc(explicacao)}</p></div>"
    )


def placar_html(acertos: int, total: int) -> str:
    pct = round(100 * acertos / total) if total else 0
    frase = "Mandou bem!" if pct >= 80 else "Bom começo — revise os erros abaixo." if pct >= 50 else "Vale reler o material e tentar de novo."
    return (
        f'<div class="nm-card nm-placar"><div class="nm-num">{acertos}/{total}</div>'
        f'<div class="nm-rotulo">acertos · {pct}%</div><p style="margin-top:.6rem">{_esc(frase)}</p></div>'
    )


def passo_html(numero: int, titulo: str, explicacao: str, exemplo: str | None) -> str:
    exemplo_html = f"<pre>{_esc(exemplo)}</pre>" if exemplo else ""
    return (
        f'<div class="nm-passo"><div class="nm-bola">{numero}</div>'
        f"<div><h4>{_esc(titulo)}</h4><p>{_esc(explicacao)}</p>{exemplo_html}</div></div>"
    )


def vazio_html() -> str:
    return (
        '<div class="nm-vazio"><strong>Como funciona</strong>'
        "<ol><li>Envie um PDF, Markdown ou TXT — ou use a base de exemplo (guia de Power BI).</li>"
        "<li>Diga o tema que o material deve cobrir.</li>"
        "<li>Escolha o perfil do estudante e o formato, e gere.</li></ol></div>"
    )
