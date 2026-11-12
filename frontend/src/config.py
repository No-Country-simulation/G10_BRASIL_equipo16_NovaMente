"""Configuração do frontend: caminhos, modo de execução e opções dos menus.

Os valores dos menus espelham o que a `ai_stack` aceita HOJE (ai_stack/schemas.py e
rag_pipeline.validar_nivel). Quando a IA passar a aceitar novos perfis/formatos, basta
acrescentar aqui.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

PASTA_FRONTEND = Path(__file__).resolve().parents[1]
RAIZ_REPO = PASTA_FRONTEND.parent
PASTA_FIXTURES = PASTA_FRONTEND / "fixtures"
PASTA_UPLOADS = RAIZ_REPO / "data" / "uploads"

load_dotenv(PASTA_FRONTEND / ".env")

MODO = os.getenv("NOVAMENTE_MODO", "mock").strip().lower()
MAX_UPLOAD_MB = int(os.getenv("NOVAMENTE_MAX_UPLOAD_MB", "10"))

EXTENSOES_SUPORTADAS = (".pdf", ".md", ".txt")

# rótulo mostrado na tela -> valor enviado à ai_stack
PERFIS = {
    "Iniciante": "iniciante",
    "Intermediário": "intermediario",
}
FORMATOS = {
    "Flashcards": "flashcards",
    "Quiz": "quiz",
    "Tutorial": "tutorial",
}

# Cenários prontos para a demonstração: mesmo documento (guia de Power BI já indexado
# em docs/rag/base-de-conhecimento), perfis e formatos diferentes.
CENARIOS_DEMO = [
    {
        "nome": "Iniciante · Flashcards",
        "pergunta": "O que é o Power Query e para que serve?",
        "perfil": "Iniciante",
        "formato": "Flashcards",
    },
    {
        "nome": "Intermediário · Quiz",
        "pergunta": "Como funcionam os relacionamentos e o esquema estrela no Power BI?",
        "perfil": "Intermediário",
        "formato": "Quiz",
    },
    {
        "nome": "Iniciante · Tutorial",
        "pergunta": "Como criar uma medida DAX simples?",
        "perfil": "Iniciante",
        "formato": "Tutorial",
    },
]
