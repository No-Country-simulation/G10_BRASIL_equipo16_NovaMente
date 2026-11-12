"""Único módulo do frontend que fala com a `ai_stack`.

Reaproveita exatamente as funções de `ai_stack/main.py` (main após o PR #5, nomes em português):
carregar_documento → dividir_documentos_em_blocos → obter_modelo_embeddings → criar_banco_vetorial → gerar_resposta_rag.

As importações são feitas dentro dos métodos para que o modo mock funcione sem
torch/chroma/groq instalados, e para que uma renomeação na ai_stack quebre só aqui.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.config import EXTENSOES_SUPORTADAS, PASTA_UPLOADS, RAIZ_REPO
from src.servico import ErroServico

MENSAGENS = {
    "sem_dependencias": (
        "As bibliotecas da ai_stack não estão instaladas. Na raiz do repositório rode "
        "`python -m pip install -r requirements.txt`, ou use NOVAMENTE_MODO=mock."
    ),
    "sem_chave": (
        "A variável GROQ_API_KEY não está definida. Crie um arquivo .env na raiz do repositório "
        "com GROQ_API_KEY=... (peça a chave ao responsável pela ai_stack)."
    ),
    "json_invalido": "A IA devolveu uma resposta fora do formato esperado. Tente novamente ou reformule o tema.",
    "rede": "Não foi possível falar com o provedor da LLM (Groq). Verifique a conexão e tente de novo.",
}


def _garantir_raiz_no_path() -> None:
    raiz = str(RAIZ_REPO)
    if raiz not in sys.path:
        sys.path.insert(0, raiz)


class ServicoIA:
    nome = "ai_stack · Groq"

    def __init__(self, pasta_uploads: Path = PASTA_UPLOADS) -> None:
        self.pasta_uploads = pasta_uploads
        self._db = None
        self._embeddings = None

    # ---------- carregamento ----------

    def _verificar_ambiente(self) -> None:
        load_dotenv(RAIZ_REPO / ".env")
        if not os.getenv("GROQ_API_KEY"):
            raise ErroServico(MENSAGENS["sem_chave"])
        _garantir_raiz_no_path()

    def _embeddings_model(self):
        if self._embeddings is None:
            try:
                from ai_stack.ingestion.embeddings import obter_modelo_embeddings
            except ImportError as e:
                raise ErroServico(MENSAGENS["sem_dependencias"]) from e
            self._embeddings = obter_modelo_embeddings()
        return self._embeddings

    def _abrir_base_existente(self):
        """Abre o Chroma persistido (base de Power BI indexada por `python -m ai_stack.main`)."""
        try:
            from langchain_chroma import Chroma

            from ai_stack.config import CHROMA_DB_PATH
        except ImportError as e:
            raise ErroServico(MENSAGENS["sem_dependencias"]) from e
        return Chroma(embedding_function=self._embeddings_model(), persist_directory=CHROMA_DB_PATH)

    # ---------- API do serviço ----------

    def indexar(self, nome_arquivo: str, dados: bytes) -> str:
        self._verificar_ambiente()
        nome = Path(nome_arquivo).name
        if not nome.lower().endswith(EXTENSOES_SUPORTADAS):
            raise ErroServico(f"Arquivo não suportado. Use {', '.join(EXTENSOES_SUPORTADAS)}.")
        if not dados:
            raise ErroServico("O arquivo enviado está vazio.")

        try:
            from ai_stack.ingestion.chunking import dividir_documentos_em_blocos
            from ai_stack.ingestion.document_identity import (
                calcular_versao_documento,
                gerar_identificador_documento_local,
            )
            from ai_stack.ingestion.loader import carregar_documento
            from ai_stack.ingestion.vector_store import criar_banco_vetorial
        except ImportError as e:
            raise ErroServico(MENSAGENS["sem_dependencias"]) from e

        self.pasta_uploads.mkdir(parents=True, exist_ok=True)
        destino = self.pasta_uploads / nome
        destino.write_bytes(dados)

        try:
            document_id = gerar_identificador_documento_local(destino, self.pasta_uploads)
            versao = calcular_versao_documento(destino)
            documentos = carregar_documento(destino, document_id, versao)
            chunks = dividir_documentos_em_blocos(documentos)
            self._db = criar_banco_vetorial(chunks, self._embeddings_model())
        except ValueError as e:
            raise ErroServico(f"Não foi possível processar o arquivo: {e}") from e
        return nome

    def gerar(self, pergunta: str, perfil: str, formato: str) -> dict:
        self._verificar_ambiente()
        if not pergunta.strip():
            raise ErroServico("Digite o tema ou a pergunta que o material deve cobrir.")
        if self._db is None:
            self._db = self._abrir_base_existente()

        try:
            from ai_stack.rag_pipeline import gerar_resposta_rag
        except ImportError as e:
            raise ErroServico(MENSAGENS["sem_dependencias"]) from e

        try:
            return gerar_resposta_rag(pergunta.strip(), self._db, perfil, formato)
        except ValueError as e:
            # rag_pipeline levanta ValueError para JSON inválido / resposta vazia / schema inválido
            raise ErroServico(f"{MENSAGENS['json_invalido']} (detalhe: {e})") from e
        except Exception as e:  # erros de rede/autenticação do cliente Groq
            nome_erro = type(e).__name__
            if "groq" in type(e).__module__ or "Connection" in nome_erro or "Timeout" in nome_erro:
                raise ErroServico(f"{MENSAGENS['rede']} ({nome_erro})") from e
            raise
