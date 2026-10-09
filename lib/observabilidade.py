"""Logging estruturado com correlation_id por execução."""
from __future__ import annotations

import logging
import time
import uuid
from contextlib import contextmanager
from typing import Iterator

log = logging.getLogger('assistente.ml')
if not log.handlers:
    logging.basicConfig(level=logging.INFO, format='%(message)s')


def novo_correlation_id() -> str:
    return str(uuid.uuid4())


@contextmanager
def no_evento(nome: str, correlation_id: str) -> Iterator[None]:
    t0 = time.perf_counter()
    log.info('{"event":"start","node":"%s","correlation_id":"%s"}', nome, correlation_id)
    try:
        yield
    finally:
        dt = int((time.perf_counter() - t0) * 1000)
        log.info(
            '{"event":"end","node":"%s","correlation_id":"%s","duration_ms":%s}',
            nome,
            correlation_id,
            dt,
        )
