"""Funções puras que geram os arquivos de download. Não importam streamlit."""

import csv
import io
import json

from src.modelos import Flashcard, PassoTutorial, QuestaoQuiz, Requisicao, ResultadoIA

PERFIL_ENUNCIADO = {"iniciante": "Iniciante", "intermediario": "Intermediario"}
FORMATO_ENUNCIADO = {"flashcards": "Flashcards", "quiz": "Quiz", "tutorial": "Tutorial"}


def _itens_enunciado(itens) -> list[dict]:
    saida = []
    for item in itens:
        if isinstance(item, Flashcard):
            saida.append({"tipo": "flashcard", "frente": item.frente, "verso": item.verso})
        elif isinstance(item, QuestaoQuiz):
            saida.append(
                {
                    "tipo": "quiz",
                    "pergunta": item.pergunta,
                    "opcoes": [o.texto for o in item.opcoes],
                    "resposta_correta": item.resposta_correta.texto,
                    "justificativa": item.justificativa,
                }
            )
        elif isinstance(item, PassoTutorial):
            saida.append(
                {"tipo": "passo", "titulo": item.titulo, "explicacao": item.explicacao, "exemplo": item.exemplo}
            )
    return saida


def _avaliacao_qualidade(resultado: ResultadoIA) -> dict:
    revisao = resultado.revisao
    if revisao is None:
        return {
            "ancoragem_fonte_score": None,
            "clareza_pedagogica": "Nao avaliada",
            "observacoes": "Formato sem revisão automática nesta versão.",
        }
    total = len(resultado.pacote.itens) if resultado.pacote else 1
    com_problema = len({p.item_id for p in revisao.problemas})
    return {
        "ancoragem_fonte_score": round(max(0.0, 1 - com_problema / max(total, 1)), 2),
        "clareza_pedagogica": "Alta" if revisao.aprovado else "Media",
        "observacoes": revisao.resumo,
    }


def para_json_enunciado(resultado: ResultadoIA, requisicao: Requisicao) -> dict:
    """Traduz o resultado da ai_stack para o JSON de saída definido no enunciado (pt-BR)."""
    if resultado.pacote is None:
        return {"status": "erro", "mensagem": resultado.mensagem or resultado.status}
    pacote = resultado.pacote
    m = pacote.metadados
    return {
        "status": "sucesso",
        "metadados": {
            "perfil_aplicado": PERFIL_ENUNCIADO.get(m.perfil, m.perfil),
            "formato_gerado": FORMATO_ENUNCIADO.get(m.formato, m.formato),
            "nicho_setor": "Geral",
            "tempo_estimado_estudo_minutos": m.tempo_estudo_minutos,
            "conceitos_chave": list(m.conceitos_chave),
            "pre_requisitos": list(m.pre_requisitos),
        },
        "conteudo_adaptado": {
            "titulo": pacote.titulo,
            "introducao_contextualizada": pacote.introducao or "",
            "itens": _itens_enunciado(pacote.itens),
        },
        "avaliacao_qualidade": _avaliacao_qualidade(resultado),
        "fontes": [{"arquivo": f.arquivo, "pagina": f.pagina} for f in resultado.fontes],
        "requisicao": {
            "documento_titulo": requisicao.titulo_documento or requisicao.nome_arquivo or "base de conhecimento",
            "pergunta": requisicao.pergunta,
        },
        "armazenamento_oci": {"status_upload": "nao_configurado"},
    }


def para_json_texto(dados: dict) -> str:
    return json.dumps(dados, ensure_ascii=False, indent=2)


def para_markdown(resultado: ResultadoIA) -> str:
    pacote = resultado.pacote
    if pacote is None:
        return f"# Sem conteúdo\n\n{resultado.mensagem or ''}\n"
    m = pacote.metadados
    linhas = [f"# {pacote.titulo}", ""]
    if pacote.introducao:
        linhas += [pacote.introducao, ""]
    linhas += [
        f"- **Perfil:** {m.perfil}",
        f"- **Formato:** {m.formato}",
        f"- **Tempo estimado:** {m.tempo_estudo_minutos} min",
        f"- **Conceitos-chave:** {', '.join(m.conceitos_chave) or '—'}",
        "",
    ]
    for i, item in enumerate(pacote.itens, start=1):
        if isinstance(item, Flashcard):
            linhas += [f"## Cartão {i}", f"**Frente:** {item.frente}", "", f"**Verso:** {item.verso}", ""]
        elif isinstance(item, QuestaoQuiz):
            linhas += [f"## Questão {i}", item.pergunta, ""]
            for o in item.opcoes:
                marca = "✅" if o.id == item.id_correta else "▫️"
                linhas.append(f"- {marca} {o.texto}")
            linhas += ["", f"> {item.justificativa}", ""]
        elif isinstance(item, PassoTutorial):
            linhas += [f"## Passo {i}: {item.titulo}", item.explicacao, ""]
            if item.exemplo:
                linhas += ["```", item.exemplo, "```", ""]
    if resultado.fontes:
        linhas += ["## Fontes", *[f"- {f.arquivo} (página {f.pagina})" for f in resultado.fontes], ""]
    return "\n".join(linhas)


def para_csv_anki(resultado: ResultadoIA) -> str:
    """CSV de duas colunas (frente, verso) separadas por tabulação — importável no Anki."""
    pacote = resultado.pacote
    buffer = io.StringIO()
    escritor = csv.writer(buffer, delimiter="\t", lineterminator="\n")
    if pacote is None:
        return ""
    for item in pacote.itens:
        if isinstance(item, Flashcard):
            escritor.writerow([item.frente, item.verso])
        elif isinstance(item, QuestaoQuiz):
            escritor.writerow([item.pergunta, f"{item.resposta_correta.texto} — {item.justificativa}"])
        elif isinstance(item, PassoTutorial):
            escritor.writerow([item.titulo, item.explicacao])
    return buffer.getvalue()
