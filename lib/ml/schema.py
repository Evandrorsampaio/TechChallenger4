"""Contrato Pydantic de features de risco gestacional (24 variáveis)."""
from __future__ import annotations

import re
import sqlite3
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from lib.config import REFERENCE_DATE

N_FEATURES = 24
DATASET_VERSION = 'v1.0.0'

OBRIGATORIAS: tuple[str, ...] = (
    'idade',
    'imc_pre_gestacional',
    'ig_semanas',
    'gestacoes',
    'partos',
    'abortos',
    'pas_mmhg',
    'pad_mmhg',
    'has_cronica',
    'diabetes_previo',
    'gemelaridade',
)

OPCIONAIS: tuple[str, ...] = (
    'escolaridade_anos',
    'cesareas_previas',
    'natimorto_previo',
    'pre_eclampsia_previa',
    'intervalo_interpartal_meses',
    'hemoglobina_g_dl',
    'glicemia_jejum_mg_dl',
    'proteinuria_fita',
    'cardiopatia',
    'nefropatia',
    'tev_previo',
    'tabagismo',
    'infeccao_sexual_ativa',
)

FEATURES: tuple[str, ...] = OBRIGATORIAS + OPCIONAIS

PROTEINURIA_NIVEIS: tuple[str, ...] = ('ausente', 'traços', '1+', '2+', '3+')

_GPA = re.compile(r'^G(\d+)P(\d+)A(\d+)$', re.IGNORECASE)


class DadosIncompletosError(Exception):
    """Campo obrigatório ausente. Não imputa; devolve a lista de faltantes."""

    def __init__(self, campos_faltantes: list[str]):
        self.campos_faltantes = list(campos_faltantes)
        msg = (
            'Campos obrigatórios ausentes: '
            + ', '.join(self.campos_faltantes)
            + '. Completar os dados e resubmeter. Valores obrigatórios não são imputados.'
        )
        super().__init__(msg)


class DominioInvalidoError(ValueError):
    """Valor fora da faixa ou inconsistência obstétrica/pressórica."""

    def __init__(self, campo: str, valor: Any, faixa: str, detalhe: str | None = None):
        self.campo = campo
        self.valor = valor
        self.faixa = faixa
        extra = f' {detalhe}' if detalhe else ''
        super().__init__(
            f'Campo `{campo}` recebeu {valor!r}, fora da faixa aceita ({faixa}).{extra}'
        )


class GestanteFeatures(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)

    idade: int = Field(..., ge=13, le=50)
    imc_pre_gestacional: float = Field(..., ge=15.0, le=55.0)
    ig_semanas: int = Field(..., ge=4, le=42)
    gestacoes: int = Field(..., ge=1, le=12)
    partos: int = Field(..., ge=0, le=10)
    abortos: int = Field(..., ge=0, le=6)
    pas_mmhg: int = Field(..., ge=80, le=200)
    pad_mmhg: int = Field(..., ge=50, le=130)
    has_cronica: bool
    diabetes_previo: bool
    gemelaridade: bool

    escolaridade_anos: int | None = Field(default=None, ge=0, le=20)
    cesareas_previas: int | None = Field(default=None, ge=0, le=5)
    natimorto_previo: bool | None = None
    pre_eclampsia_previa: bool | None = None
    intervalo_interpartal_meses: float | None = Field(default=None, ge=0, le=300)
    hemoglobina_g_dl: float | None = Field(default=None, ge=5.0, le=16.0)
    glicemia_jejum_mg_dl: float | None = Field(default=None, ge=60.0, le=200.0)
    proteinuria_fita: str | None = None
    cardiopatia: bool | None = None
    nefropatia: bool | None = None
    tev_previo: bool | None = None
    tabagismo: bool | None = None
    infeccao_sexual_ativa: bool | None = None

    @field_validator('proteinuria_fita')
    @classmethod
    def _proteinuria(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in PROTEINURIA_NIVEIS:
            raise ValueError(
                f'Campo `proteinuria_fita` recebeu {v!r}, fora da faixa aceita '
                f'({"|".join(PROTEINURIA_NIVEIS)}).'
            )
        return v

    @model_validator(mode='after')
    def _invariantes(self) -> GestanteFeatures:
        if self.partos + self.abortos > self.gestacoes:
            raise ValueError(
                f'Campo `partos`/`abortos` recebeu partos={self.partos}, abortos={self.abortos}, '
                f'gestacoes={self.gestacoes}, fora da faixa aceita '
                f'(partos + abortos <= gestacoes).'
            )
        if self.pad_mmhg >= self.pas_mmhg:
            raise ValueError(
                f'Campo `pad_mmhg` recebeu {self.pad_mmhg}, fora da faixa aceita '
                f'(pad_mmhg < pas_mmhg={self.pas_mmhg}).'
            )
        return self

    def campos_imputaveis_ausentes(self) -> list[str]:
        return [nome for nome in OPCIONAIS if getattr(self, nome) is None]

    def para_registro(self) -> dict[str, Any]:
        return self.model_dump()


def _formatar_validation_error(exc: ValidationError) -> DominioInvalidoError:
    err = exc.errors()[0]
    loc = '.'.join(str(x) for x in err.get('loc', ())) or 'payload'
    inp = err.get('input', None)
    return DominioInvalidoError(loc, inp, 'ver contrato v1.0.0', err.get('msg'))


def parse_gestante(data: dict[str, Any]) -> GestanteFeatures:
    """Valida o payload de inferência.

    Obrigatório ausente ou None → DadosIncompletosError (nunca imputa).
    Extra, tipo ou faixa → DominioInvalidoError / ValidationError.
    """
    if not isinstance(data, dict):
        raise DominioInvalidoError('payload', type(data).__name__, 'objeto JSON/dict')
    faltantes = [c for c in OBRIGATORIAS if c not in data or data[c] is None]
    if faltantes:
        raise DadosIncompletosError(faltantes)
    try:
        return GestanteFeatures.model_validate(data)
    except ValidationError as exc:
        raise _formatar_validation_error(exc) from exc


def _parse_gpa(texto: str | None) -> tuple[int | None, int | None, int | None]:
    if not texto:
        return None, None, None
    m = _GPA.match(texto.strip().replace(' ', ''))
    if not m:
        return None, None, None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def _idade_de_nascimento(data_nascimento: str | date | None, hoje: date) -> int | None:
    if data_nascimento is None:
        return None
    if isinstance(data_nascimento, str):
        nasc = date.fromisoformat(data_nascimento[:10])
    else:
        nasc = data_nascimento
    anos = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))
    return anos


def _ig_de_dum(dum: str | date | None, hoje: date) -> int | None:
    if dum is None:
        return None
    if isinstance(dum, str):
        d = date.fromisoformat(dum[:10])
    else:
        d = dum
    dias = (hoje - d).days
    if dias < 0:
        return None
    semanas = dias // 7
    if 4 <= semanas <= 42:
        return semanas
    return None


def features_de_paciente(
    conn: sqlite3.Connection,
    paciente_id: int,
    hoje: date | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Monta payload parcial a partir de hospital.db.

    Nunca infere IMC, PA, HAS, diabetes ou gemelaridade. Declara ausentes.
    """
    ref = hoje or REFERENCE_DATE
    pac = conn.execute(
        'SELECT paciente_id, data_nascimento FROM pacientes WHERE paciente_id = ?',
        (paciente_id,),
    ).fetchone()
    if pac is None:
        raise KeyError(f'paciente_id={paciente_id} não encontrado')
    pront = conn.execute(
        'SELECT g_p_a, dum FROM prontuario_gineco WHERE paciente_id = ?',
        (paciente_id,),
    ).fetchone()
    payload: dict[str, Any] = {}
    idade = _idade_de_nascimento(pac['data_nascimento'], ref)
    if idade is not None and 13 <= idade <= 50:
        payload['idade'] = idade
    g = p = a = None
    if pront:
        g, p, a = _parse_gpa(pront['g_p_a'])
        ig = _ig_de_dum(pront['dum'], ref)
        if ig is not None:
            payload['ig_semanas'] = ig
    if g is not None and g >= 1:
        payload['gestacoes'] = min(max(g, 1), 12)
    if p is not None:
        payload['partos'] = min(max(p, 0), 10)
    if a is not None:
        payload['abortos'] = min(max(a, 0), 6)
    ausentes = [c for c in OBRIGATORIAS if c not in payload]
    return payload, ausentes


assert len(FEATURES) == N_FEATURES
assert len(OBRIGATORIAS) == 11
assert len(OPCIONAIS) == 13
