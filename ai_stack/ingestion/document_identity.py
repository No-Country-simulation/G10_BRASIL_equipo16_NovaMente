import hashlib
from pathlib import Path
import uuid



def gerar_document_id_local( file: Path, raiz_documentos: Path) -> str:

    file = file.resolve()
    raiz_documentos = raiz_documentos.resolve()

    if not file.exists():
        raise FileNotFoundError(f"Ficheiro inexistente: {file}")

    if not file.is_file():
        raise ValueError(f"{file} não é um ficheiro válido")

    if not raiz_documentos.is_dir():
        raise NotADirectoryError(raiz_documentos)

    try:
        caminho_relativo = file.relative_to(raiz_documentos)
    except ValueError as erro:
        raise ValueError( "O ficheiro deve estar dentro da pasta de documentos" ) from erro

    identificador = uuid.uuid5(
        uuid.NAMESPACE_URL,
        f"novamente:{caminho_relativo.as_posix().casefold()}"
    )

    return str(identificador)

def calcular_versao_documento(file : Path):
    if not file.exists():
        raise FileNotFoundError(f"Ficheiro inexistente : {file}")
    if not file.is_file():
        raise ValueError(f"{file} não é um arquivo")

    hasher= hashlib.sha256()

    with open(file,"rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()
