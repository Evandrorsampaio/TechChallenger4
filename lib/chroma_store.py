"""Abre o índice Chroma fora do Google Drive.

O SQLite do Chroma (`chroma.sqlite3`) em `files/chroma/`, montado em
`/content/drive`, falha na leitura com SQLITE_IOERR_READ (código 266).
A mensagem chega na triagem como
``Error getting collection: Database error: ... (code: 266) disk I/O error``
porque o primeiro `similarity_search` é que chama `get_collection`.

O índice continua persistido no Drive. Cada sessão copia a pasta para o
disco local da VM e abre o Chroma a partir dessa cópia.
"""
from __future__ import annotations

import shutil
from pathlib import Path


def no_google_drive(caminho: str | Path) -> bool:
    texto = str(caminho).replace("\\", "/").lower()
    return "/content/drive" in texto or "mydrive" in texto


def diretorio_local(origem: str | Path, destino: str | Path | None = None) -> Path:
    """Devolve um diretório em disco local com o índice pronto para abrir.

    Se `origem` já não estiver no Drive, devolve o próprio caminho.
    """
    origem = Path(origem)
    if not no_google_drive(origem):
        return origem

    destino = Path(destino or "/content/chroma_local")
    sqlite = destino / "chroma.sqlite3"
    if sqlite.is_file() and destino.exists():
        return destino

    if not origem.exists():
        raise FileNotFoundError(
            f"Índice Chroma não encontrado em {origem}. "
            "Rode 06_indexar_protocolos.ipynb para gerá-lo."
        )
    if destino.exists():
        shutil.rmtree(destino)
    print(f"Copiando Chroma do Drive para {destino} (SQLite no Drive gera erro 266).")
    try:
        shutil.copytree(origem, destino)
    except OSError as exc:
        raise OSError(
            f"Não consegui ler {origem}. O arquivo no Drive está ilegível. "
            "Apague files/chroma e rode de novo o notebook 06: ele grava o "
            "índice no disco local e só depois copia para o Drive."
        ) from exc
    if not (destino / "chroma.sqlite3").is_file():
        raise FileNotFoundError(
            f"A cópia em {destino} não tem chroma.sqlite3. "
            "O índice no Drive está incompleto; rode o notebook 06 de novo."
        )
    return destino


def publicar(local: str | Path, destino_drive: str | Path) -> Path:
    """Copia um índice já fechado no disco local para a pasta persistente do Drive."""
    local = Path(local)
    destino = Path(destino_drive)
    if not (local / "chroma.sqlite3").is_file():
        raise FileNotFoundError(f"Nada para publicar: {local} não tem chroma.sqlite3.")
    if destino.exists():
        shutil.rmtree(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(local, destino)
    return destino
