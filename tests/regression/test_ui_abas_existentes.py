"""Regressão das abas Gradio (Fase 3 + 6ª aba)."""
import inspect
from pathlib import Path

from lib.ui import build_ui


def test_assinatura_build_ui_intacta():
    sig = inspect.signature(build_ui)
    assert list(sig.parameters)[:4] == ['agent', 'conn', 'default_usuario', 'workflows']


def test_ui_tem_seis_abas_principais():
    src = (Path(__file__).resolve().parents[2] / 'lib' / 'ui.py').read_text(encoding='utf-8')
    principais = [
        'Consulta livre',
        'Triagem Ginecológica',
        'Detecção de Violência',
        'Atendimento Obstétrico',
        'Prevenção e Rastreamento',
        'Risco Gestacional (ML)',
    ]
    for titulo in principais:
        assert titulo in src
