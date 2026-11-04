
from collections import defaultdict

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from ai_stack.config import CHROMA_DB_PATH


def validar_ids_dos_blocos(blocos: list[Document]) -> set[str]:

    if not blocos:
        raise ValueError("A lista de blocos não pode estar vazia")

    ids_blocos = []
    versoes_por_documento = {}

    for indice, bloco in enumerate(blocos):

        if not isinstance(bloco, Document):
            raise TypeError(
                f"O elemento na posição {indice} não é um Document"
            )

        metadados = bloco.metadata

        if not isinstance(metadados, dict):
            raise TypeError("Os metadados devem ser um dicionário")

        for campo in (
            "chunk_id",
            "document_id",
            "document_version"
        ):
            valor = metadados.get(campo)

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

        id_bloco = metadados["chunk_id"]
        id_documento = metadados["document_id"]
        versao_documento = metadados["document_version"]

        # Um documento não pode ter versões diferentes
        # na mesma operação de ingestão.
        if id_documento in versoes_por_documento:

            if versoes_por_documento[id_documento] != versao_documento:
                raise ValueError(
                    f"Documento {id_documento} possui versões diferentes"
                )

        else:
            versoes_por_documento[id_documento] = versao_documento

        ids_blocos.append(id_bloco)

    # Impedir IDs duplicados na entrada
    if len(ids_blocos) != len(set(ids_blocos)):
        raise ValueError("Existem blocos com IDs duplicados")

    return set(ids_blocos)


def criar_banco_vetorial(
    blocos: list[Document],
    modelo_embeddings: HuggingFaceEmbeddings
) -> Chroma:

    if modelo_embeddings is None:
        raise ValueError("O modelo de embeddings não pode ser None")

    validar_ids_dos_blocos(blocos)

    # Abrir ou criar a base vetorial persistente
    banco_vetorial = Chroma(
        embedding_function=modelo_embeddings,
        persist_directory=CHROMA_DB_PATH
    )

    # Agrupar os blocos por documento
    blocos_por_documento = defaultdict(list)

    for bloco in blocos:
        id_documento = bloco.metadata["document_id"]
        blocos_por_documento[id_documento].append(bloco)

    # Processar cada documento individualmente
    for id_documento, blocos_documento in blocos_por_documento.items():

        versao_documento = blocos_documento[0].metadata["document_version"]

        ids_recebidos = [
            bloco.metadata["chunk_id"]
            for bloco in blocos_documento
        ]

        conjunto_ids_recebidos = set(ids_recebidos)

        # Consultar apenas os registos deste documento
        dados_atuais = banco_vetorial.get(
            where={"document_id": id_documento},
            include=["metadatas"]
        )

        ids_existentes = set(dados_atuais.get("ids", []))

        metadados_existentes = dados_atuais.get("metadatas") or []

        versoes_existentes = {
            metadado.get("document_version")
            for metadado in metadados_existentes
            if isinstance(metadado, dict)
        }

        # Verificar se o documento já está completamente
        # sincronizado com a versão recebida.
        if (
            ids_existentes == conjunto_ids_recebidos
            and versoes_existentes == {versao_documento}
        ):
            print(f"Documento {id_documento}: sem alterações.")
            continue

        blocos_por_id = {
            bloco.metadata["chunk_id"]: bloco
            for bloco in blocos_documento
        }

        # 1. Inserir blocos que ainda não existem.
        ids_novos = [
            id_bloco
            for id_bloco in ids_recebidos
            if id_bloco not in ids_existentes
        ]

        if ids_novos:
            banco_vetorial.add_documents(
                documents=[
                    blocos_por_id[id_bloco]
                    for id_bloco in ids_novos
                ],
                ids=ids_novos
            )

        # 2. Actualizar blocos existentes com o mesmo ID,
        # caso a composição ou os metadados tenham mudado.
        ids_comuns = [
            id_bloco
            for id_bloco in ids_recebidos
            if id_bloco in ids_existentes
        ]

        if ids_comuns:
            banco_vetorial.update_documents(
                ids=ids_comuns,
                documents=[
                    blocos_por_id[id_bloco]
                    for id_bloco in ids_comuns
                ]
            )

        # 3. Remover blocos antigos ou que desapareceram
        # da versão actual do documento.
        ids_antigos = ids_existentes - conjunto_ids_recebidos

        if ids_antigos:
            banco_vetorial.delete(ids=list(ids_antigos))

        print(
            f"Documento {id_documento} sincronizado. "
            f"Versão: {versao_documento}"
        )

    return banco_vetorial
