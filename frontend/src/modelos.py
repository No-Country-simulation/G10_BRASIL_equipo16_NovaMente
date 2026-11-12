"""Modelos internos da interface.

A tela nunca lê o JSON da IA diretamente: o `adaptador` converte a resposta da `ai_stack`
para estas estruturas. Se o schema da IA mudar, só o adaptador precisa mudar.
"""

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Requisicao:
    pergunta: str
    perfil: str  # valor aceito pela ai_stack: "iniciante" | "intermediario"
    formato: str  # "flashcards" | "quiz" | "tutorial"
    nome_arquivo: str | None = None
    titulo_documento: str | None = None


@dataclass(frozen=True)
class Flashcard:
    id: str
    frente: str
    verso: str


@dataclass(frozen=True)
class OpcaoQuiz:
    id: str
    texto: str


@dataclass(frozen=True)
class QuestaoQuiz:
    id: str
    pergunta: str
    opcoes: tuple[OpcaoQuiz, ...]
    id_correta: str
    justificativa: str

    @property
    def resposta_correta(self) -> OpcaoQuiz:
        return next(opcao for opcao in self.opcoes if opcao.id == self.id_correta)


@dataclass(frozen=True)
class PassoTutorial:
    titulo: str
    explicacao: str
    exemplo: str | None = None


@dataclass(frozen=True)
class Metadados:
    perfil: str
    formato: str
    conceitos_chave: tuple[str, ...]
    tempo_estudo_minutos: int
    pre_requisitos: tuple[str, ...]


@dataclass(frozen=True)
class Fonte:
    arquivo: str
    pagina: str


@dataclass(frozen=True)
class ProblemaRevisao:
    item_id: str
    item_tipo: str
    categoria: str
    descricao: str
    evidencia: str
    sugestao: str


@dataclass(frozen=True)
class Revisao:
    status: Literal["approved", "correction_required"]
    resumo: str
    problemas: tuple[ProblemaRevisao, ...] = ()

    @property
    def aprovado(self) -> bool:
        return self.status == "approved"


@dataclass(frozen=True)
class Pacote:
    titulo: str
    metadados: Metadados
    itens: tuple[Flashcard, ...] | tuple[QuestaoQuiz, ...] | tuple[PassoTutorial, ...]
    introducao: str | None = None


StatusIA = Literal["success", "insufficient_context", "requires_manual_review"]


@dataclass(frozen=True)
class ResultadoIA:
    status: StatusIA
    pacote: Pacote | None
    fontes: tuple[Fonte, ...] = ()
    revisao: Revisao | None = None
    mensagem: str | None = None
    resposta_bruta: dict = field(default_factory=dict)
