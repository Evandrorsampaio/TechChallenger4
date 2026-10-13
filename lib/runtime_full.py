"""Resolução de caminhos e de 4-bit para o perfil Llama + Chroma.

Sem variável de ambiente, lê `files/` na raiz do repositório (cópia local do Drive).
O compose full define os caminhos montados em `/drive/files`. Não importa torch.
"""
from __future__ import annotations

import os
from pathlib import Path

from lib.config import REPO_ROOT
from lib.llm import _latest_adapter_dir

COLLECTION_PADRAO = 'protocolos_saude_mulher'
EMBEDDING_PADRAO = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'


def resolver_adapter(adapter_dir: str | None = None, finetune_base: str | None = None) -> Path | None:
    """Aceita a pasta `adapter_final` ou o diretório pai das runs de fine-tuning."""
    if adapter_dir:
        pasta = Path(adapter_dir)
        if (pasta / 'adapter_config.json').is_file():
            return pasta
        encontrada = _latest_adapter_dir(pasta)
        if encontrada is not None:
            return encontrada
    if finetune_base:
        return _latest_adapter_dir(finetune_base)
    return None


def decidir_4bit(cuda_disponivel: bool, pedido: str | None = None) -> bool:
    """4-bit só com CUDA. Pedido vazio segue o hardware; `0` desliga; `1` exige GPU."""
    if pedido is None or pedido.strip() == '':
        return cuda_disponivel
    if pedido.strip() == '0':
        return False
    return cuda_disponivel


def device_embeddings(cuda_disponivel: bool) -> str:
    return 'cuda' if cuda_disponivel else 'cpu'


def files_locais() -> Path:
    return REPO_ROOT / 'files'


def _caminho_env(chave: str) -> str:
    return os.environ.get(chave, '').strip()


def chroma_dir_configurado() -> Path:
    bruto = _caminho_env('CHROMA_PATH')
    if bruto:
        return Path(bruto)
    return files_locais() / 'chroma'


def hospital_db_full() -> Path:
    bruto = _caminho_env('HOSPITAL_DB_PATH')
    if bruto:
        return Path(bruto)
    return files_locais() / 'hospital.db'


def origem_adapter() -> tuple[str | None, str | None]:
    """`(adapter_dir, finetune_base)` para `resolver_adapter`.

    Vazio usa `files/finetune`, de onde sai a run `llama32-3b-saude-mulher_*` mais recente.
    """
    explicito = _caminho_env('ADAPTER_DIR')
    finetune = _caminho_env('FINETUNE_DIR')
    if explicito:
        return explicito, finetune or None
    if finetune:
        return None, finetune
    return None, str(files_locais() / 'finetune')


def pedido_4bit() -> str | None:
    if 'USE_4BIT' not in os.environ:
        return None
    return os.environ.get('USE_4BIT')
