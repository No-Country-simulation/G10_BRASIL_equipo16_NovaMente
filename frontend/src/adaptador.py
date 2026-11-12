"""Converte o retorno de `ai_stack.rag_pipeline.generate_rag_response` em modelos internos.

Formato esperado (ai_stack, branch main):
{
  "status": "success" | "insufficient_context" | "requires_manual_review",
  "answer": EducationalPackage | None,   # {"metadata": {...}, "content": {...}}
  "sources": [{"source": str, "page": int|str}],
  "message": str | None,
  "review_report": ReviewReport | None   # {"status", "summary", "issues": [...]}
}
"""

from typing import Any

from src.modelos import (
    Flashcard,
    Fonte,
    Metadados,
    OpcaoQuiz,
    Pacote,
    PassoTutorial,
    ProblemaRevisao,
    QuestaoQuiz,
    ResultadoIA,
    Revisao,
)

STATUS_VALIDOS = ("success", "insufficient_context", "requires_manual_review")


class RespostaInvalidaError(Exception):
    """A resposta da IA não tem a estrutura esperada."""


def _exigir(dados: dict, chave: str, contexto: str) -> Any:
    if chave not in dados:
        raise RespostaInvalidaError(f"Campo obrigatório ausente em {contexto}: '{chave}'")
    return dados[chave]


def _adaptar_metadados(metadata: dict) -> Metadados:
    return Metadados(
        perfil=str(_exigir(metadata, "profile_applied", "metadata")),
        formato=str(_exigir(metadata, "format_generated", "metadata")),
        conceitos_chave=tuple(metadata.get("key_concepts") or ()),
        tempo_estudo_minutos=int(_exigir(metadata, "study_time_minutes", "metadata")),
        pre_requisitos=tuple(metadata.get("prerequisites") or ()),
    )


def _adaptar_itens(formato: str, content: dict):
    if formato == "flashcards":
        return tuple(
            Flashcard(id=str(c["card_id"]), frente=c["front"], verso=c["back"])
            for c in _exigir(content, "cards", "content")
        )
    if formato == "quiz":
        return tuple(
            QuestaoQuiz(
                id=str(q["question_id"]),
                pergunta=q["question"],
                opcoes=tuple(OpcaoQuiz(id=str(o["option_id"]), texto=o["text"]) for o in q["options"]),
                id_correta=str(q["correct_option_id"]),
                justificativa=q["justification"],
            )
            for q in _exigir(content, "questions", "content")
        )
    if formato == "tutorial":
        return tuple(
            PassoTutorial(titulo=s["title"], explicacao=s["explanation"], exemplo=s.get("example"))
            for s in _exigir(content, "steps", "content")
        )
    raise RespostaInvalidaError(f"Formato desconhecido: '{formato}'")


def adaptar_pacote(answer: dict) -> Pacote:
    metadata = _exigir(answer, "metadata", "answer")
    content = _exigir(answer, "content", "answer")
    metadados = _adaptar_metadados(metadata)
    try:
        itens = _adaptar_itens(metadados.formato, content)
    except (KeyError, TypeError) as e:
        raise RespostaInvalidaError(f"Item de conteúdo malformado: {e}") from e
    if not itens:
        raise RespostaInvalidaError("O conteúdo veio sem itens")
    return Pacote(
        titulo=str(_exigir(content, "title", "content")),
        introducao=content.get("introduction"),
        metadados=metadados,
        itens=itens,
    )


def adaptar_revisao(review_report: dict | None) -> Revisao | None:
    if not review_report:
        return None
    status = _exigir(review_report, "status", "review_report")
    if status not in ("approved", "correction_required"):
        raise RespostaInvalidaError(f"Status de revisão desconhecido: '{status}'")
    problemas = tuple(
        ProblemaRevisao(
            item_id=str(p.get("item_id", "")),
            item_tipo=str(p.get("item_type", "")),
            categoria=str(p.get("category", "")),
            descricao=str(p.get("description", "")),
            evidencia=str(p.get("evidence", "")),
            sugestao=str(p.get("suggestion", "")),
        )
        for p in review_report.get("issues") or ()
    )
    return Revisao(status=status, resumo=str(review_report.get("summary", "")), problemas=problemas)


def adaptar_fontes(sources: list | None) -> tuple[Fonte, ...]:
    return tuple(
        Fonte(arquivo=str(s.get("source", "Desconhecido")), pagina=str(s.get("page", "?")))
        for s in sources or ()
    )


def adaptar_resposta(resposta: dict) -> ResultadoIA:
    if not isinstance(resposta, dict):
        raise RespostaInvalidaError("A resposta da IA deveria ser um objeto JSON")
    status = _exigir(resposta, "status", "resposta")
    if status not in STATUS_VALIDOS:
        raise RespostaInvalidaError(f"Status desconhecido: '{status}'")

    answer = resposta.get("answer")
    pacote = adaptar_pacote(answer) if status == "success" else None
    if status == "success" and pacote is None:
        raise RespostaInvalidaError("Status 'success' sem conteúdo em 'answer'")

    return ResultadoIA(
        status=status,
        pacote=pacote,
        fontes=adaptar_fontes(resposta.get("sources")),
        revisao=adaptar_revisao(resposta.get("review_report")),
        mensagem=resposta.get("message"),
        resposta_bruta=resposta,
    )
