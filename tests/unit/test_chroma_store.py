"""O índice Chroma no Google Drive não pode ser aberto no lugar."""
from pathlib import Path

from lib.chroma_store import diretorio_local, no_google_drive, publicar


def test_caminho_local_nao_e_copiado(tmp_path: Path):
    origem = tmp_path / "chroma"
    origem.mkdir()
    (origem / "chroma.sqlite3").write_bytes(b"ok")
    assert diretorio_local(origem) == origem


def test_drive_e_copiado_para_disco_local(tmp_path: Path):
    origem = tmp_path / "content" / "drive" / "MyDrive" / "files" / "chroma"
    origem.mkdir(parents=True)
    (origem / "chroma.sqlite3").write_bytes(b"sqlite")
    (origem / "segmento.bin").write_bytes(b"vec")
    destino = tmp_path / "chroma_local"

    assert no_google_drive(origem)
    copiado = diretorio_local(origem, destino)

    assert copiado == destino
    assert (destino / "chroma.sqlite3").read_bytes() == b"sqlite"
    assert (destino / "segmento.bin").read_bytes() == b"vec"
    de_novo = diretorio_local(origem, destino)
    assert de_novo == destino


def test_publicar_substitui_a_pasta_do_drive(tmp_path: Path):
    local = tmp_path / "local"
    local.mkdir()
    (local / "chroma.sqlite3").write_bytes(b"novo")
    drive = tmp_path / "drive" / "chroma"
    drive.mkdir(parents=True)
    (drive / "chroma.sqlite3").write_bytes(b"velho")

    publicado = publicar(local, drive)

    assert publicado == drive
    assert (drive / "chroma.sqlite3").read_bytes() == b"novo"
