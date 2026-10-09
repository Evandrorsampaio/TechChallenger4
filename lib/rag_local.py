"""Retriever lexical para o perfil demo-cpu (sem Chroma / embeddings).

O corpus versionado em ``artifacts/rag/protocolos_subset.json`` é um recorte
didático com ``doc_id`` estável. Não substitui o índice Chroma do Colab.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORPUS_PADRAO = ROOT / 'artifacts' / 'rag' / 'protocolos_subset.json'

_STOP = {
    'a', 'o', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'das', 'dos', 'e', 'em',
    'para', 'com', 'por', 'na', 'no', 'nas', 'nos', 'ao', 'à', 'que', 'se', 'ou',
    'the', 'of', 'and',
}


def _tokens(texto: str) -> set[str]:
    partes = re.findall(r'[a-záàâãéêíóôõúç0-9]{3,}', (texto or '').lower())
    return {p for p in partes if p not in _STOP}


@dataclass
class DocumentoLocal:
    page_content: str
    metadata: dict[str, Any]


class RetrieverLocal:
    """Busca por sobreposição de termos + bônus de categoria no metadado."""

    def __init__(self, chunks: list[dict[str, Any]]):
        self._chunks = list(chunks)

    def invoke(self, query: str) -> list[DocumentoLocal]:
        q = _tokens(query)
        ranqueados: list[tuple[float, DocumentoLocal]] = []
        for ch in self._chunks:
            texto = ch.get('text') or ''
            meta = {
                'doc_id': ch.get('doc_id', '?'),
                'category': ch.get('category', '?'),
                'chunk_id': ch.get('chunk_id', '?'),
                'name': ch.get('name', ''),
            }
            corpo = f"{texto} {meta['name']} {meta['doc_id']}"
            toks = _tokens(corpo)
            if q:
                overlap = len(q & toks)
                if overlap == 0:
                    continue
                score = overlap / max(len(q), 1)
            else:
                score = 0.01
            cat = (query or '').lower()
            if meta['category'] and meta['category'] in cat:
                score += 0.25
            ranqueados.append((score, DocumentoLocal(page_content=texto, metadata=meta)))
        ranqueados.sort(key=lambda x: x[0], reverse=True)
        if ranqueados:
            return [d for _, d in ranqueados[:8]]
        # fallback: devolve o primeiro chunk para o fluxo não ficar sem fonte
        ch = self._chunks[0]
        return [
            DocumentoLocal(
                page_content=ch.get('text') or '',
                metadata={
                    'doc_id': ch.get('doc_id', '?'),
                    'category': ch.get('category', '?'),
                    'chunk_id': ch.get('chunk_id', '?'),
                },
            )
        ]


def carregar_corpus(caminho: Path | None = None) -> list[dict[str, Any]]:
    path = caminho or CORPUS_PADRAO
    return json.loads(path.read_text(encoding='utf-8'))


def build_local_retriever(caminho: Path | None = None) -> RetrieverLocal:
    return RetrieverLocal(carregar_corpus(caminho))
