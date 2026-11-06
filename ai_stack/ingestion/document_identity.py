
import hashlib
from pathlib import Path
import uuid


def gerar_identificador_documento_local( caminho_arquivo: Path,raiz_documentos: Path) -> str:

    caminho_arquivo = caminho_arquivo.resolve()
    raiz_documentos = raiz_documentos.resolve()

    if not caminho_arquivo.exists():
        raise FileNotFoundError(f"Ficheiro inexistente: {caminho_arquivo}")

    if not caminho_arquivo.is_file():
        raise ValueError(f"{caminho_arquivo} não é um ficheiro válido")

    if not raiz_documentos.is_dir():
        raise NotADirectoryError(f"Raiz de documentos inválida : {raiz_documentos}")

    try:
        caminho_relativo = caminho_arquivo.relative_to(raiz_documentos)

    except ValueError as erro:
        raise ValueError("O ficheiro deve estar dentro da pasta de documentos") from erro

    identificador = uuid.uuid5(
        uuid.NAMESPACE_URL,
        f"novamente:{caminho_relativo.as_posix().casefold()}"
    )

    return str(identificador)


def calcular_versao_documento(caminho_arquivo: Path):

    if not caminho_arquivo.exists():
        raise FileNotFoundError(
            f"Ficheiro inexistente: {caminho_arquivo}"
        )

    if not caminho_arquivo.is_file():
        raise ValueError(
            f"{caminho_arquivo} não é um arquivo"
        )

    calculador_hash = hashlib.sha256()

    with open(caminho_arquivo, "rb") as arquivo:
        while bloco_bytes := arquivo.read(8192):
            calculador_hash.update(bloco_bytes)

    return calculador_hash.hexdigest()
