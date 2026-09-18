import inspect

from lib.ui import build_ui


def test_assinatura_build_ui_intacta():
    sig = inspect.signature(build_ui)
    assert list(sig.parameters)[:4] == ['agent', 'conn', 'default_usuario', 'workflows']
