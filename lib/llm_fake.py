"""Dublê determinístico de chat (sem BaseChatModel — evita conflito de versões LangChain)."""
from __future__ import annotations

from typing import Any


class _Msg:
    def __init__(self, content: str):
        self.content = content


class FakeChatModel:
    """Respostas fixas por padrão no prompt. Mesma entrada → mesma saída."""

    def _gerar_texto(self, prompt: str) -> str:
        baixo = prompt.lower()
        if 'alto_risco' in baixo or 'alto risco' in baixo:
            return (
                'As variáveis que mais contribuíram para esta classificação foram as listadas no payload. '
                'Encaminhar ao pré-natal de alto risco conforme o resultado do modelo. '
                'Não alterar as probabilidades informadas.'
            )
        if 'incompleto' in baixo or 'ausentes' in baixo:
            return 'Não houve predição. Completar os campos obrigatórios listados no payload.'
        if 'bypass' in baixo or 'emerg' in baixo:
            return 'Encaminhamento imediato por regra determinística de alarme obstétrico.'
        return (
            'Síntese determinística do payload. Resultado de apoio à decisão. '
            'As variáveis que mais contribuíram para esta classificação foram as do payload.'
        )

    def invoke(self, input: Any, config: Any = None, **kwargs: Any) -> Any:
        if isinstance(input, str):
            return _Msg(self._gerar_texto(input))
        if isinstance(input, list):
            texto = '\n'.join(getattr(m, 'content', str(m)) for m in input)
            return _Msg(self._gerar_texto(texto))
        return _Msg(self._gerar_texto(str(input)))

    def bind_tools(self, tools, **kwargs):
        return self
