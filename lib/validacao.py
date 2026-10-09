"""Validação determinística de respostas do LLM + coerência numérica com o payload ML."""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Reexporta o validador da Fase 3 (permanece em referencias/).
_REF = Path(__file__).resolve().parent.parent / 'referencias'
if str(_REF) not in sys.path:
    sys.path.insert(0, str(_REF))

from validador_resposta_llm import (  # noqa: E402
    ResultadoValidacao,
    ValidadorDeterministico,
    ValidadorLLM,
)

__all__ = [
    'ResultadoValidacao',
    'ValidadorDeterministico',
    'ValidadorLLM',
    'verificar_coerencia_numerica',
]


def _numerais(texto: str) -> list[float]:
    achados = re.findall(r'(?<![\w.])(\d+,\d+|\d+\.\d+|\d+)(?![\w.])', texto)
    out = []
    for a in achados:
        out.append(float(a.replace(',', '.')))
    return out


def verificar_coerencia_numerica(texto: str, payload: dict, tol: float = 0.005) -> ResultadoValidacao:
    """Descarta o texto se numerais ou rótulo contradisserem o payload."""
    violacoes: list[str] = []
    avisos: list[str] = []
    pred = str(payload.get('prediction', ''))
    baixo = texto.lower()
    if pred == 'alto_risco' and re.search(r'\bhabitual\b', baixo) and not re.search(r'alto[_\s-]?risco', baixo):
        violacoes.append('Texto contradiz o rótulo alto_risco')
    if pred == 'habitual' and re.search(r'alto[_\s-]?risco', baixo) and 'não' not in baixo:
        # permite mencionar a classe negativa
        if re.search(r'classifica[cç][aã]o[:\s]+alto', baixo):
            violacoes.append('Texto contradiz o rótulo habitual')
    permitidos = []
    probs = payload.get('probabilities') or {}
    for v in probs.values():
        try:
            permitidos.append(float(v))
        except (TypeError, ValueError):
            pass
    if payload.get('threshold') is not None:
        permitidos.append(float(payload['threshold']))
    for n in _numerais(texto):
        if n > 100:  # anos, mmHg citados do caso — não do modelo
            continue
        if 0 <= n <= 1.5 or 0 <= n <= 100:
            ok = False
            for p in permitidos:
                if abs(n - p) <= tol or abs(n - p * 100) <= 1:
                    ok = True
                    break
            if 0 <= n <= 1 and not ok and permitidos:
                # numeral de probabilidade sem correspondente
                if any(abs(n - p) <= 0.05 for p in permitidos):
                    ok = True
            if not ok and 0 < n < 1:
                violacoes.append(f'Numeral {n} ausente do payload')
    aprovada = not violacoes
    return ResultadoValidacao(
        aprovada=aprovada,
        violacoes=violacoes,
        avisos=avisos,
        disclaimer_sugerido='' if aprovada else 'Texto do LLM descartado por divergência numérica.',
    )
