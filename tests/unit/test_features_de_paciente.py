from __future__ import annotations

from datetime import date

from lib.db import connect, init_schema
from lib.ml.schema import features_de_paciente


def test_ponte_declara_obrigatorios_ausentes(tmp_path):
    db = tmp_path / 'h.db'
    conn = connect(db)
    init_schema(conn)
    conn.execute(
        "INSERT INTO pacientes (paciente_id, nome, data_nascimento, cpf_hash, cadastro_em) "
        "VALUES (1, 'Teste', '1995-03-10', 'abc', '2026-01-01')"
    )
    conn.execute(
        "INSERT INTO prontuario_gineco (paciente_id, g_p_a, dum) VALUES (1, 'G2P1A0', '2025-12-01')"
    )
    conn.commit()
    payload, ausentes = features_de_paciente(conn, 1, hoje=date(2026, 5, 22))
    assert 'idade' in payload
    assert 'gestacoes' in payload
    assert payload['gestacoes'] == 2
    assert payload['partos'] == 1
    assert payload['abortos'] == 0
    for campo in (
        'imc_pre_gestacional',
        'pas_mmhg',
        'pad_mmhg',
        'has_cronica',
        'diabetes_previo',
        'gemelaridade',
    ):
        assert campo in ausentes
        assert campo not in payload
    conn.close()
