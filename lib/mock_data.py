"""Gerador de dados sintéticos para o hospital mock.

Cenários cobertos (deliberadamente diversos para testar fluxos):
- gestantes (DUM recente, sem ciclos)
- climatério / pós-menopausa (sem ciclos, sem método contraceptivo)
- mamografia atrasada (50-69a sem exame recente)
- papanicolau atrasado (25-64a)
- vítimas de violência (com notificação SINAN)
- usuárias de método contraceptivo com ciclos regulares
"""
from __future__ import annotations

import hashlib
import random
from datetime import date, datetime, timedelta
from typing import Iterable

from faker import Faker

from lib.config import REFERENCE_DATE

TODAY = REFERENCE_DATE

TIPOS_VIOLENCIA = ['fisica', 'psicologica', 'sexual', 'patrimonial', 'moral']
METODOS_CONTRACEPTIVOS = [
    'COC (etinilestradiol + drospirenona)',
    'POP (desogestrel)',
    'DIU de cobre',
    'DIU hormonal (levonorgestrel)',
    'Implante subdérmico (etonogestrel)',
    'Injetável trimestral (medroxiprogesterona)',
    'Preservativo masculino',
    'Laqueadura tubária',
    'Nenhum',
]

# Lista enxuta de medicamentos comuns em saúde da mulher
MEDICAMENTOS_BASE = [
    ('levonorgestrel + etinilestradiol', 'Microvlar / Ciclo 21',
     'Contracepção hormonal combinada oral',
     'Tabagismo + idade ≥35a; HAS não controlada; histórico de TEV; enxaqueca com aura', 'X', 'cautela'),
    ('desogestrel', 'Cerazette',
     'Contracepção em lactantes e contraindicação a estrogênio',
     'Câncer hormonio-dependente; sangramento vaginal inexplicado', 'X', 'compativel'),
    ('medroxiprogesterona acetato', 'Depo-Provera',
     'Contracepção injetável trimestral',
     'Gestação; sangramento inexplicado; câncer de mama', 'X', 'compativel'),
    ('ácido fólico', 'Folacin',
     'Prevenção de defeito de tubo neural; suplementação periconcepcional',
     'Hipersensibilidade ao fármaco', 'A', 'compativel'),
    ('sulfato ferroso', 'Noripurum / Sulfato Ferroso',
     'Anemia ferropriva; suplementação na gestação',
     'Hemocromatose; anemias não-ferroprivas', 'A', 'compativel'),
    ('metronidazol', 'Flagyl',
     'Vaginose bacteriana; tricomoníase',
     'Primeiro trimestre de gestação (uso oral); álcool concomitante', 'B', 'cautela'),
    ('clindamicina vaginal', 'Dalacin V',
     'Vaginose bacteriana',
     'Hipersensibilidade à clindamicina; colite pseudomembranosa prévia', 'B', 'compativel'),
    ('fluconazol', 'Zoltec',
     'Candidíase vulvovaginal',
     'Gestação (doses altas); QT longo', 'D', 'cautela'),
    ('nitrofurantoína', 'Macrodantina',
     'ITU baixa não complicada',
     'Clearance creatinina <60; G6PD deficiente; gestação ≥36 semanas', 'B', 'compativel'),
    ('amoxicilina', 'Amoxil',
     'ITU em gestantes; profilaxia de endocardite',
     'Alergia a penicilinas', 'B', 'compativel'),
    ('misoprostol', 'Cytotec (uso hospitalar)',
     'Aborto retido; indução de parto; abortamento legal',
     'Cesárea prévia (na indução); gestação tópica viável desejada', 'X', 'compativel'),
    ('ocitocina', 'Syntocinon',
     'Indução e condução de parto; atonia uterina pós-parto',
     'Desproporção céfalo-pélvica; sofrimento fetal sem indicação de parto', 'C', 'compativel'),
    ('sertralina', 'Zoloft',
     'Depressão; transtorno de ansiedade; TPM disfórica',
     'Uso concomitante de IMAO; hipersensibilidade', 'C', 'compativel'),
    ('escitalopram', 'Lexapro',
     'Depressão; transtorno de ansiedade generalizada',
     'Uso concomitante de IMAO; QT longo', 'C', 'cautela'),
    ('fluoxetina', 'Prozac',
     'Depressão; bulimia nervosa; TOC',
     'IMAO; hipersensibilidade', 'C', 'cautela'),
    ('estradiol transdérmico', 'Estradot',
     'Terapia hormonal da menopausa; sintomas vasomotores',
     'Câncer de mama; TEV; doença hepática ativa', 'X', 'cautela'),
    ('tibolona', 'Livial',
     'Sintomas climatéricos em mulher pós-menopausa',
     'Câncer hormonio-dependente; sangramento vaginal inexplicado', 'X', 'contraindicado'),
    ('ácido tranexâmico', 'Transamin',
     'Sangramento uterino aumentado',
     'TEV ativo; insuficiência renal grave', 'B', 'compativel'),
    ('progesterona micronizada', 'Utrogestan',
     'Insuficiência lútea; suporte na gestação',
     'Doença hepática ativa; sangramento vaginal inexplicado', 'B', 'compativel'),
    ('levonorgestrel 1.5mg', 'Postinor',
     'Contracepção de emergência (até 72h pós-relação)',
     'Gestação confirmada; hipersensibilidade', 'X', 'cautela'),
]


def hash_cpf(cpf_str: str) -> str:
    return hashlib.sha256(cpf_str.encode()).hexdigest()[:16]


def _idade(dn: date) -> int:
    return (TODAY - dn).days // 365


def _data_aleatoria_entre(inicio: date, fim: date, rng: random.Random) -> date:
    delta = (fim - inicio).days
    if delta <= 0:
        return inicio
    return inicio + timedelta(days=rng.randint(0, delta))


def gerar_pacientes(n: int, fake: Faker, rng: random.Random) -> list[dict]:
    pacientes = []
    # Distribuição etária deliberada para cobrir cenários
    faixas = (
        [(18, 24)] * int(n * 0.10) +
        [(25, 39)] * int(n * 0.35) +
        [(40, 49)] * int(n * 0.20) +
        [(50, 65)] * int(n * 0.25) +
        [(66, 75)] * int(n * 0.10)
    )
    while len(faixas) < n:
        faixas.append((25, 49))

    for i, (idade_min, idade_max) in enumerate(faixas, start=1):
        idade = rng.randint(idade_min, idade_max)
        dn = TODAY - timedelta(days=idade * 365 + rng.randint(0, 364))
        pacientes.append({
            'paciente_id': i,
            'nome': fake.name_female(),
            'data_nascimento': dn.isoformat(),
            'cpf_hash': hash_cpf(fake.cpf()),
            'convenio': rng.choice(['SUS', 'SUS', 'SUS', 'Unimed', 'Bradesco', 'Particular']),
            'cadastro_em': _data_aleatoria_entre(date(2020, 1, 1), TODAY, rng).isoformat(),
        })
    return pacientes


def _gpa(idade: int, rng: random.Random) -> str:
    if idade < 20:
        g = rng.choices([0, 1], weights=[8, 2])[0]
    elif idade < 30:
        g = rng.choices([0, 1, 2, 3], weights=[3, 4, 2, 1])[0]
    elif idade < 45:
        g = rng.choices([0, 1, 2, 3, 4], weights=[2, 4, 4, 2, 1])[0]
    else:
        g = rng.choices([0, 1, 2, 3, 4, 5], weights=[1, 2, 4, 3, 2, 1])[0]
    a = rng.choices([0, 1, 2], weights=[7, 2, 1])[0] if g > 0 else 0
    p = max(0, g - a)
    return f'G{g}P{p}A{a}'


def _cenario_paciente(paciente: dict, rng: random.Random) -> str:
    """Atribui um cenário clínico para guiar geração coerente."""
    idade = _idade(date.fromisoformat(paciente['data_nascimento']))
    if idade >= 50:
        return rng.choices(
            ['climaterio', 'mamografia_atrasada', 'normal'],
            weights=[3, 2, 5],
        )[0]
    if 25 <= idade <= 35:
        return rng.choices(
            ['gestante', 'contraceptivo', 'papanicolau_atrasado', 'normal'],
            weights=[2, 4, 2, 4],
        )[0]
    return rng.choices(['contraceptivo', 'normal'], weights=[3, 7])[0]


def gerar_prontuario(paciente: dict, cenario: str, rng: random.Random) -> dict:
    idade = _idade(date.fromisoformat(paciente['data_nascimento']))
    menarca = rng.randint(10, 14)

    if cenario == 'gestante':
        dum = TODAY - timedelta(weeks=rng.randint(6, 36))
        metodo = 'Nenhum'
    elif cenario == 'climaterio' or idade >= 55:
        dum = TODAY - timedelta(days=rng.randint(365, 365 * 5)) if rng.random() < 0.7 else None
        metodo = 'Nenhum'
    else:
        dum = TODAY - timedelta(days=rng.randint(1, 35))
        metodo = (rng.choice(METODOS_CONTRACEPTIVOS) if cenario == 'contraceptivo'
                  else rng.choices(METODOS_CONTRACEPTIVOS, weights=[2, 1, 2, 2, 2, 1, 3, 1, 4])[0])

    hist_fam = rng.choices(
        ['', 'Mãe com câncer de mama aos 58a', 'Tia materna com câncer de colo',
         'HAS e DM2 na família', 'Sem antecedentes relevantes'],
        weights=[3, 2, 1, 2, 4],
    )[0]

    return {
        'paciente_id': paciente['paciente_id'],
        'menarca_idade': menarca,
        'g_p_a': _gpa(idade, rng),
        'dum': dum.isoformat() if dum else None,
        'metodo_contraceptivo': metodo,
        'historico_familiar': hist_fam,
        'observacoes': '',
    }


def gerar_exames(paciente: dict, cenario: str, rng: random.Random) -> list[dict]:
    idade = _idade(date.fromisoformat(paciente['data_nascimento']))
    exames: list[dict] = []
    pid = paciente['paciente_id']

    # Papanicolau: 25-64a — histórico anual nos 2 primeiros anos, depois trienal
    if 25 <= idade <= 64:
        if cenario == 'papanicolau_atrasado':
            anos_atras = rng.uniform(4.0, 7.0)
            ultima = TODAY - timedelta(days=int(anos_atras * 365))
            exames.append({
                'paciente_id': pid,
                'tipo': 'papanicolau',
                'data_realizacao': ultima.isoformat(),
                'resultado': 'NIC I / LSIL',
                'proximo_recomendado': (ultima + timedelta(days=3 * 365)).isoformat(),
            })
        else:
            anos = sorted({rng.uniform(0.3, 1.0), rng.uniform(1.5, 2.5), rng.uniform(3.5, 5.5)})
            for a in anos:
                if a > (idade - 25):
                    continue
                d = TODAY - timedelta(days=int(a * 365))
                exames.append({
                    'paciente_id': pid,
                    'tipo': 'papanicolau',
                    'data_realizacao': d.isoformat(),
                    'resultado': rng.choices(
                        ['Negativo para lesão intraepitelial', 'ASC-US', 'LSIL'],
                        weights=[8, 1, 1],
                    )[0],
                    'proximo_recomendado': (d + timedelta(days=3 * 365)).isoformat(),
                })

    # Mamografia: 50-69a bienal
    if 50 <= idade <= 69:
        if cenario == 'mamografia_atrasada':
            anos_atras = rng.uniform(3.0, 6.0)
            d = TODAY - timedelta(days=int(anos_atras * 365))
            exames.append({
                'paciente_id': pid,
                'tipo': 'mamografia',
                'data_realizacao': d.isoformat(),
                'resultado': 'BI-RADS 2 (achados benignos)',
                'proximo_recomendado': (d + timedelta(days=2 * 365)).isoformat(),
            })
        else:
            for a in (rng.uniform(0.5, 1.8), rng.uniform(2.5, 4.0)):
                d = TODAY - timedelta(days=int(a * 365))
                exames.append({
                    'paciente_id': pid,
                    'tipo': 'mamografia',
                    'data_realizacao': d.isoformat(),
                    'resultado': rng.choices(
                        ['BI-RADS 1 (sem achados)', 'BI-RADS 2 (benigno)', 'BI-RADS 3 (provavelmente benigno)'],
                        weights=[6, 3, 1],
                    )[0],
                    'proximo_recomendado': (d + timedelta(days=2 * 365)).isoformat(),
                })

    # USG pélvica se gestante
    if cenario == 'gestante':
        d = TODAY - timedelta(days=rng.randint(7, 60))
        exames.append({
            'paciente_id': pid,
            'tipo': 'usg_pelvica',
            'data_realizacao': d.isoformat(),
            'resultado': f'Gestação tópica única, IG compatível, BCF presentes',
            'proximo_recomendado': (d + timedelta(days=30)).isoformat(),
        })

    return exames


def gerar_ciclos(paciente: dict, cenario: str, rng: random.Random) -> list[dict]:
    idade = _idade(date.fromisoformat(paciente['data_nascimento']))
    if cenario in ('gestante', 'climaterio') or idade >= 55:
        return []
    pid = paciente['paciente_id']
    ciclos = []
    duracao_padrao = rng.randint(26, 31)
    # últimos 12 ciclos
    cursor = TODAY - timedelta(days=rng.randint(1, duracao_padrao))
    for _ in range(12):
        ciclos.append({
            'paciente_id': pid,
            'data_inicio': cursor.isoformat(),
            'duracao_dias': max(2, min(8, rng.gauss(5, 1))) if False else rng.randint(3, 7),
            'sintomas': rng.choice(['', 'cólica leve', 'cefaleia pré-menstrual', 'mastalgia', '']),
        })
        cursor -= timedelta(days=duracao_padrao + rng.randint(-3, 3))
    return ciclos


def gerar_registros_violencia(pacientes: list[dict], rng: random.Random,
                              n_vitimas: int = 10) -> list[dict]:
    selecionadas = rng.sample(pacientes, k=min(n_vitimas, len(pacientes)))
    registros = []
    for p in selecionadas:
        n_eventos = rng.choices([1, 2, 3], weights=[6, 3, 1])[0]
        for _ in range(n_eventos):
            data = TODAY - timedelta(days=rng.randint(7, 365 * 3))
            tipo = rng.choice(TIPOS_VIOLENCIA)
            registros.append({
                'paciente_id': p['paciente_id'],
                'tipo': tipo,
                'data_atendimento': data.isoformat(),
                'notificado_sinan': 1,
                'encaminhamentos': rng.choice([
                    'Centro de Referência da Mulher; Psicologia',
                    'Ligue 180 orientado; Delegacia da Mulher',
                    'CAPS; assistência social',
                    'Profilaxia ISTs; serviço social; psicologia',
                ]),
                'observacoes': '',
            })
    return registros


def populate(conn, n_pacientes: int = 50, seed: int = 42,
             faker_locale: str = 'pt_BR', verbose: bool = True) -> dict:
    """Popula todas as tabelas com dados sintéticos. Retorna sumário."""
    rng = random.Random(seed)
    fake = Faker(faker_locale)
    Faker.seed(seed)

    pacientes = gerar_pacientes(n_pacientes, fake, rng)
    cenarios = {p['paciente_id']: _cenario_paciente(p, rng) for p in pacientes}

    conn.executemany(
        'INSERT INTO pacientes VALUES (:paciente_id,:nome,:data_nascimento,:cpf_hash,:convenio,:cadastro_em)',
        pacientes,
    )

    prontuarios = [gerar_prontuario(p, cenarios[p['paciente_id']], rng) for p in pacientes]
    conn.executemany(
        'INSERT INTO prontuario_gineco '
        '(paciente_id,menarca_idade,g_p_a,dum,metodo_contraceptivo,historico_familiar,observacoes) '
        'VALUES (:paciente_id,:menarca_idade,:g_p_a,:dum,:metodo_contraceptivo,:historico_familiar,:observacoes)',
        prontuarios,
    )

    todos_exames = []
    for p in pacientes:
        todos_exames.extend(gerar_exames(p, cenarios[p['paciente_id']], rng))
    if todos_exames:
        conn.executemany(
            'INSERT INTO exames (paciente_id,tipo,data_realizacao,resultado,proximo_recomendado) '
            'VALUES (:paciente_id,:tipo,:data_realizacao,:resultado,:proximo_recomendado)',
            todos_exames,
        )

    todos_ciclos = []
    for p in pacientes:
        todos_ciclos.extend(gerar_ciclos(p, cenarios[p['paciente_id']], rng))
    if todos_ciclos:
        conn.executemany(
            'INSERT INTO ciclos_menstruais (paciente_id,data_inicio,duracao_dias,sintomas) '
            'VALUES (:paciente_id,:data_inicio,:duracao_dias,:sintomas)',
            todos_ciclos,
        )

    registros = gerar_registros_violencia(pacientes, rng)
    if registros:
        conn.executemany(
            'INSERT INTO registros_violencia '
            '(paciente_id,tipo,data_atendimento,notificado_sinan,encaminhamentos,observacoes) '
            'VALUES (:paciente_id,:tipo,:data_atendimento,:notificado_sinan,:encaminhamentos,:observacoes)',
            registros,
        )

    meds = [{
        'nome_principio_ativo': m[0], 'nome_comercial': m[1],
        'indicacoes': m[2], 'contraindicacoes': m[3],
        'categoria_gestacao': m[4], 'categoria_lactacao': m[5],
    } for m in MEDICAMENTOS_BASE]
    conn.executemany(
        'INSERT INTO medicamentos '
        '(nome_principio_ativo,nome_comercial,indicacoes,contraindicacoes,categoria_gestacao,categoria_lactacao) '
        'VALUES (:nome_principio_ativo,:nome_comercial,:indicacoes,:contraindicacoes,:categoria_gestacao,:categoria_lactacao)',
        meds,
    )

    conn.commit()

    sumario = {
        'pacientes': len(pacientes),
        'prontuarios': len(prontuarios),
        'exames': len(todos_exames),
        'ciclos': len(todos_ciclos),
        'registros_violencia': len(registros),
        'medicamentos': len(meds),
        'cenarios': {c: sum(1 for v in cenarios.values() if v == c) for c in set(cenarios.values())},
    }
    if verbose:
        for k, v in sumario.items():
            print(f'  {k}: {v}')
    return sumario
