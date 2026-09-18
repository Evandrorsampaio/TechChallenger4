from __future__ import annotations

import re
from pathlib import Path

PADROES = (
    re.compile(r'hf_[A-Za-z0-9]{20,}'),
    re.compile(r'sk-[A-Za-z0-9]{20,}'),
    re.compile(r'AKIA[0-9A-Z]{16}'),
    re.compile(r'password\s*='),
)

IGNORAR = {
    '.git',
    '.venv',
    'venv',
    '__pycache__',
    'artifacts',
    'node_modules',
    '.pytest_cache',
}


def test_repositorio_sem_segredos():
    raiz = Path('.')
    ofensores: list[str] = []
    for path in raiz.rglob('*'):
        if any(p in IGNORAR for p in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in {'.py', '.yml', '.yaml', '.toml', '.json'}:
            if path.name not in {'.env.example', 'Dockerfile', '.gitignore', 'requirements.txt', 'requirements-ml.txt', 'requirements-llm.txt'}:
                continue
        try:
            texto = path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, OSError):
            continue
        for pat in PADROES:
            if pat.search(texto):
                ofensores.append(f'{path}: {pat.pattern}')
    assert ofensores == []
