
from collections import defaultdict

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from ai_stack.config import CHROMA_DB_PATH


def validar_chunks_ids(chunks: list[Document]) -> set[str]:

    if not chunks:
        raise ValueError("A lista de chunks não pode estar vazia")

    chunks_ids = []
    versoes_por_documento = {}

    for indice, chunk in enumerate(chunks):

        if not isinstance(chunk, Document):
            raise TypeError(
                f"O elemento na posição {indice} não é um Document"
            )

        metadata = chunk.metadata

        if not isinstance(metadata, dict):
            raise TypeError("Os metadados devem ser um dicionário")

        for campo in (
            "chunk_id",
            "document_id",
            "document_version"
        ):
            valor = metadata.get(campo)

            if valor is None:
                raise ValueError(
                    f"Metadado obrigatório ausente: {campo}"
                )

            if not isinstance(valor, str):
                raise TypeError(
                    f"{campo} deve ser uma string"
                )

            if not valor.strip():
                raise ValueError(
                    f"{campo} não pode estar vazio"
                )

            if valor != valor.strip():
                raise ValueError(
                    f"{campo} não pode ter espaços nas extremidades"
                )

        chunk_id = metadata["chunk_id"]
        document_id = metadata["document_id"]
        document_version = metadata["document_version"]

        # Um documento não pode ter versões diferentes
        # na mesma operação de ingestão.
        if document_id in versoes_por_documento:

            if versoes_por_documento[document_id] != document_version:
                raise ValueError(
                    f"Documento {document_id} possui versões diferentes"
                )

        else:
            versoes_por_documento[document_id] = document_version

        chunks_ids.append(chunk_id)

    # Impedir IDs duplicados na entrada
    if len(chunks_ids) != len(set(chunks_ids)):
        raise ValueError("Existem chunks com IDs duplicados")

    return set(chunks_ids)


def create_vector_db(
    chunks: list[Document],
    embedding_model: HuggingFaceEmbeddings
) -> Chroma:

    if embedding_model is None:
        raise ValueError("embedding_model não pode ser None")

    validar_chunks_ids(chunks)

    # Abrir ou criar a base vetorial persistente
    db_vector = Chroma(
        embedding_function=embedding_model,
        persist_directory=CHROMA_DB_PATH
    )

    # Agrupar os chunks por documento
    chunks_por_documento = defaultdict(list)

    for chunk in chunks:
        document_id = chunk.metadata["document_id"]
        chunks_por_documento[document_id].append(chunk)

    # Processar cada documento individualmente
    for document_id, docs_documento in chunks_por_documento.items():

        document_version = docs_documento[0].metadata["document_version"]

        ids_recebidos = [
            doc.metadata["chunk_id"]
            for doc in docs_documento
        ]

        ids_recebidos_set = set(ids_recebidos)

        # Consultar apenas os registos deste documento
        dados_atuais = db_vector.get(
            where={"document_id": document_id},
            include=["metadatas"]
        )

        ids_existentes = set(dados_atuais.get("ids", []))

        metadados_existentes = dados_atuais.get("metadatas") or []

        versoes_existentes = {
            metadata.get("document_version")
            for metadata in metadados_existentes
            if isinstance(metadata, dict)
        }

        # Verificar se o documento já está completamente
        # sincronizado com a versão recebida.
        if (
            ids_existentes == ids_recebidos_set
            and versoes_existentes == {document_version}
        ):
            print(f"Documento {document_id}: sem alterações.")
            continue

        docs_por_id = {
            doc.metadata["chunk_id"]: doc
            for doc in docs_documento
        }

        # 1. Inserir chunks que ainda não existem.
        ids_novos = [
            chunk_id
            for chunk_id in ids_recebidos
            if chunk_id not in ids_existentes
        ]

        if ids_novos:
            db_vector.add_documents(
                documents=[docs_por_id[chunk_id] for chunk_id in ids_novos],
                ids=ids_novos
            )

        # 2. Atualizar chunks existentes com o mesmo ID,
        # caso a composição ou os metadados tenham mudado.
        ids_comuns = [
            chunk_id
            for chunk_id in ids_recebidos
            if chunk_id in ids_existentes
        ]

        if ids_comuns:
            db_vector.update_documents(
                ids=ids_comuns,
                documents=[
                    docs_por_id[chunk_id]
                    for chunk_id in ids_comuns
                ]
            )

        # 3. Remover chunks antigos ou que desapareceram
        # da versão atual do documento.
        ids_antigos = ids_existentes - ids_recebidos_set

        if ids_antigos:
            db_vector.delete(ids=list(ids_antigos))

        print(
            f"Documento {document_id} sincronizado. "
            f"Versão: {document_version}"
        )

    return db_vector
