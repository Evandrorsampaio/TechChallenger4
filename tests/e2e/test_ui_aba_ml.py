from lib.ui import _render_risco_ml


def test_render_avisos():
    md = _render_risco_ml({
        'resposta_estruturada': {
            'modo': 'normal',
            'prediction': 'habitual',
            'probabilities': {'habitual': 0.8, 'alto_risco': 0.2},
            'threshold': 0.3,
            'safety_notice': 'Resultado de apoio à decisão.',
            'aviso_dados_sinteticos': 'Modelo treinado em dados sintéticos.',
            'raciocinio': ['ok'],
        }
    })
    assert 'Limiar operacional' in md
    assert 'sintéticos' in md


def test_render_degradado_primeiro():
    md = _render_risco_ml({'resposta_estruturada': {
        'modo': 'degradado',
        'prediction': 'habitual',
        'safety_notice': 'x',
        'aviso_dados_sinteticos': 'y',
    }})
    assert md.index('degradado') < md.index('Classificação') or 'Modo degradado' in md
