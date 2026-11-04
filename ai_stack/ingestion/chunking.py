
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
from ai_stack.config import CHUNK_SIZE, CHUNK_OVERLAP


def validar_documentos(documentos):
    if not documentos:
        raise ValueError('Lista de Documentos vazia ou nula')


def validar_identidade_dos_documentos(documentos: List[Document]) -> None:
    versoes_por_documento = {}

    for indice, documento in enumerate(documentos):

        # 1. Validar o tipo do documento
        if not isinstance(documento, Document):
            raise TypeError(
                f"O elemento na posição {indice} não é um Document"
            )

        # 2. Obter e validar os metadados
        metadados = documento.metadata

        if not isinstance(metadados, dict):
            raise TypeError(
                f"Os metadados do documento {indice} devem ser um dicionário"
            )

        for campo in ("document_id", "document_version"):

            # Verificar se o campo existe
            if campo not in metadados or metadados[campo] is None:
                raise ValueError(
                    f"Documento na posição {indice} sem {campo}"
                )

            valor = metadados[campo]

            # Verificar o tipo
            if not isinstance(valor, str):
                raise TypeError(
                    f"{campo} deve ser uma string"
                )

            # Verificar se está vazio
            if not valor.strip():
                raise ValueError(
                    f"{campo} não pode estar vazio"
                )

            # Evitar identificadores com espaços nas extremidades
            if valor != valor.strip():
                raise ValueError(
                    f"{campo} não deve conter espaços nas extremidades"
                )

        # 3. Obter os identificadores já validados
        id_documento = metadados["document_id"]
        versao_documento = metadados["document_version"]

        # 4. Verificar consistência das versões
        if id_documento in versoes_por_documento:

            if versoes_por_documento[id_documento] != versao_documento:
                raise ValueError(
                    f"O documento {id_documento} possui versões "
                    "diferentes na mesma ingestão"
                )

        else:
            versoes_por_documento[id_documento] = versao_documento


def dividir_documentos_em_blocos(documentos: List[Document]) -> List[Document]:
    validar_documentos(documentos)

    validar_identidade_dos_documentos(documentos)

    documentos_filtrados = [
        documento for documento in documentos
        if documento.page_content and documento.page_content.strip() != ""
    ]

    if not documentos_filtrados:
        raise ValueError('Nenhum documento com conteudo valido após filtro')

    divisor_texto = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    blocos = []

    for documento in documentos_filtrados:
        blocos_atuais = divisor_texto.split_documents([documento])

        for indice_bloco, bloco in enumerate(blocos_atuais):
            id_documento = bloco.metadata["document_id"]
            versao_documento = bloco.metadata["document_version"]

            pagina = bloco.metadata.get("page")
            referencia_pagina = (
                f"p{pagina}" if pagina is not None else "sem-pagina"
            )

            bloco.metadata["chunk_index"] = indice_bloco

            bloco.metadata["chunk_id"] = (
                f"{id_documento}_{versao_documento}_"
                f"{referencia_pagina}_c{indice_bloco}"
            )

        blocos.extend(blocos_atuais)

    return blocos
