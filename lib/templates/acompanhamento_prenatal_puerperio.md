# ACOMPANHAMENTO DE PRÉ-NATAL E PUERPÉRIO

**Instituição:** {instituicao}
**CNES:** {cnes}
**Unidade de saúde / Maternidade de referência:** {maternidade_referencia}

> Caderneta da Gestante / Sistema de Informação do Pré-Natal (SISPRENATAL).
> Protocolo baseado em: **MS — Caderneta da Gestante (2022)**, **MS — Atenção ao Pré-Natal de Baixo Risco (2012)**, **FEBRASGO — Manual de Assistência Pré-Natal (2014)**, **OMS — Recomendações sobre assistência pré-natal (2016)**.

---

## 1. Identificação da gestante

| Campo | Valor |
|---|---|
| Nome | {paciente_nome} |
| Data de nascimento | {paciente_dn} ({paciente_idade} anos) |
| ID interno / SUS Card | {paciente_id} |
| CPF | {paciente_cpf} |
| Raça/cor declarada | {raca_cor} |
| Escolaridade | {escolaridade} |
| Endereço completo | {endereco} |
| Telefone de contato | {telefone} |
| Contato de emergência | {contato_emergencia} |

## 2. Antecedentes obstétricos

| Campo | Valor |
|---|---|
| Gestações prévias (G) | {gestacoes} |
| Partos (P) — vaginais / cesáreas | {partos_vaginais} / {partos_cesareas} |
| Abortos (A) | {abortos} |
| Filhos vivos | {filhos_vivos} |
| Natimortos / óbitos neonatais | {natimortos} |
| Intercorrências em gestações anteriores | {intercorrencias_anteriores} *(DHEG / DM gestacional / prematuridade / abortamento de repetição / hemorragia / outras)* |

## 3. Antecedentes pessoais e familiares

- [ ] HAS crônica — {has_detalhes}
- [ ] Diabetes mellitus prévia — {dm_detalhes}
- [ ] Cardiopatia — {cardiopatia_detalhes}
- [ ] Doença autoimune (LES, SAF, tireoidopatia) — {autoimune_detalhes}
- [ ] Tabagismo / álcool / drogas — {tabagismo_alcool_drogas}
- [ ] Doenças infecciosas (HIV, sífilis, hepatite B/C, toxoplasmose) — {infecciosas}
- [ ] Cirurgias prévias — {cirurgias}
- [ ] Histórico familiar relevante — {historico_familiar}

## 4. Dados da gestação atual

| Campo | Valor |
|---|---|
| Data da última menstruação (DUM) | {dum} |
| Confiabilidade da DUM | {confiabilidade_dum} *(certa / incerta / desconhecida)* |
| Idade gestacional pela DUM | {ig_dum} |
| USG precoce (≤14 semanas)? | {usg_precoce} — IG corrigida: {ig_usg} |
| Data provável do parto (DPP) | {dpp} |
| Classificação de risco | {classificacao_risco} *(habitual / alto risco)* |
| Justificativa do alto risco (se aplicável) | {justificativa_alto_risco} |

> **Critérios de alto risco gestacional (MS 2012):** idade <15 ou ≥35a, IMC <18,5 ou ≥30, hipertensão prévia/gestacional, diabetes prévia/gestacional, cardiopatia, nefropatia, trombofilia, HIV/sífilis, isoimunização Rh, gemelaridade, malformação fetal, histórico de prematuridade ou óbito perinatal, violência doméstica documentada.

---

## 5. Cronograma de consultas (mínimo MS: 6 consultas)

| # | Período recomendado | Data realizada | Profissional | Observações |
|---|---|---|---|---|
| 1ª | Até 12 semanas | {consulta_1_data} | {consulta_1_profissional} | {consulta_1_obs} |
| 2ª | 16-20 semanas | {consulta_2_data} | {consulta_2_profissional} | {consulta_2_obs} |
| 3ª | 24-28 semanas | {consulta_3_data} | {consulta_3_profissional} | {consulta_3_obs} |
| 4ª | 30-32 semanas | {consulta_4_data} | {consulta_4_profissional} | {consulta_4_obs} |
| 5ª | 34-36 semanas | {consulta_5_data} | {consulta_5_profissional} | {consulta_5_obs} |
| 6ª | 38-40 semanas | {consulta_6_data} | {consulta_6_profissional} | {consulta_6_obs} |
| Pós-termo | ≥41 semanas — encaminhar avaliação hospitalar | {consulta_pos_termo} | | |

## 6. Registro evolutivo (consulta atual)

| Campo | Valor |
|---|---|
| Data | {data_consulta} |
| IG atual | {ig_atual} |
| Peso pré-gestacional | {peso_pre_gestacional} kg |
| Peso atual | {peso_atual} kg — ganho ponderal: {ganho_ponderal} kg |
| IMC pré-gestacional | {imc_pre_gestacional} ({classificacao_imc}) |
| Pressão arterial | {pa} mmHg |
| Edema | {edema} *(ausente / + / ++ / +++)* |
| Altura uterina | {altura_uterina} cm |
| Batimentos cardiofetais (BCF) | {bcf} bpm |
| Movimentação fetal | {mov_fetal} *(presente / ausente / diminuída — investigar)* |
| Apresentação fetal (≥36 sem) | {apresentacao} *(cefálica / pélvica / córmica)* |
| Queixas atuais | {queixas} |
| Conduta / orientação | {conduta} |

> **Curva de ganho ponderal esperada (MS):** IMC <18,5 → 12,5-18 kg; IMC 18,5-24,9 → 11,5-16 kg; IMC 25-29,9 → 7-11,5 kg; IMC ≥30 → 5-9 kg.

## 7. Exames laboratoriais e de imagem por trimestre

### 7.1 Primeiro trimestre (até 14 semanas)

| Exame | Solicitado | Resultado | Data |
|---|---|---|---|
| Hemograma completo | {ex_hemograma_1t} | {res_hemograma_1t} | {data_hemograma_1t} |
| Tipagem ABO/Rh + Coombs indireto | {ex_tipagem_1t} | {res_tipagem_1t} | {data_tipagem_1t} |
| Glicemia de jejum | {ex_glicemia_1t} | {res_glicemia_1t} | {data_glicemia_1t} |
| Sorologia sífilis (VDRL/RPR ou teste rápido) | {ex_sifilis_1t} | {res_sifilis_1t} | {data_sifilis_1t} |
| Sorologia HIV (teste rápido) | {ex_hiv_1t} | {res_hiv_1t} | {data_hiv_1t} |
| HBsAg + anti-HBs | {ex_hbv_1t} | {res_hbv_1t} | {data_hbv_1t} |
| Anti-HCV | {ex_hcv_1t} | {res_hcv_1t} | {data_hcv_1t} |
| Toxoplasmose IgG/IgM | {ex_toxo_1t} | {res_toxo_1t} | {data_toxo_1t} |
| EAS + urocultura | {ex_eas_1t} | {res_eas_1t} | {data_eas_1t} |
| Citologia oncótica (se >1 ano da última) | {ex_citologia_1t} | {res_citologia_1t} | {data_citologia_1t} |
| USG obstétrica precoce | {ex_usg_1t} | {res_usg_1t} | {data_usg_1t} |

### 7.2 Segundo trimestre (14-28 semanas)

| Exame | Solicitado | Resultado | Data |
|---|---|---|---|
| USG morfológica (20-24 sem) | {ex_morfologica} | {res_morfologica} | {data_morfologica} |
| TOTG 75g (24-28 sem) — rastreio DMG | {ex_totg} | {res_totg} | {data_totg} |
| Coombs indireto (se Rh-) | {ex_coombs_2t} | {res_coombs_2t} | {data_coombs_2t} |
| Repetição sorologias (sífilis, HIV, toxo) | {ex_sorologias_2t} | {res_sorologias_2t} | {data_sorologias_2t} |

### 7.3 Terceiro trimestre (≥28 semanas)

| Exame | Solicitado | Resultado | Data |
|---|---|---|---|
| Hemograma | {ex_hemograma_3t} | {res_hemograma_3t} | {data_hemograma_3t} |
| EAS + urocultura | {ex_eas_3t} | {res_eas_3t} | {data_eas_3t} |
| Repetição sorologias (sífilis, HIV) | {ex_sorologias_3t} | {res_sorologias_3t} | {data_sorologias_3t} |
| Estreptococo grupo B (swab vaginal/anal, 35-37 sem) | {ex_gbs} | {res_gbs} | {data_gbs} |
| USG obstétrica (crescimento, ILA, placenta) | {ex_usg_3t} | {res_usg_3t} | {data_usg_3t} |

## 8. Imunizações na gestação

- [ ] dTpa (tétano, difteria, coqueluche) — a partir de 20 sem, idealmente 27-36 sem — Data: {data_dtpa}
- [ ] Hepatite B — esquema completo se susceptível — Datas: {data_hepb}
- [ ] Influenza (sazonal) — em qualquer IG — Data: {data_influenza}
- [ ] COVID-19 — esquema vigente — Datas: {data_covid}
- [ ] Imunoglobulina anti-Rh (RhoGAM) — se Rh- com Coombs - e parceiro Rh+ — 28 sem e pós-parto — Data: {data_rhogam}

> ⚠️ **Contraindicadas na gestação:** vacinas de vírus vivo (sarampo, caxumba, rubéola, varicela, febre amarela — exceto epidemia, HPV).

## 9. Suplementação

- [ ] Ácido fólico 400 mcg/dia (idealmente 3 meses pré-concepcional até 12 sem) — uso atual: {acido_folico}
- [ ] Sulfato ferroso 40 mg de ferro elementar/dia (a partir de 20 sem) — uso atual: {sulfato_ferroso}
- [ ] Carbonato de cálcio 1g/dia (se baixa ingesta dietética) — uso atual: {calcio}
- [ ] Outros: {outras_suplementacoes}

## 10. Sinais de alarme orientados (gestante deve procurar serviço imediatamente)

A paciente foi orientada verbalmente e por escrito sobre os seguintes sinais que exigem avaliação hospitalar imediata:

- [ ] Sangramento vaginal de qualquer volume
- [ ] Perda de líquido amniótico
- [ ] Dor abdominal intensa ou contínua
- [ ] Cefaleia intensa que não melhora com analgésico, alterações visuais (escotomas, turvação), dor epigástrica em barra
- [ ] Crise convulsiva
- [ ] Febre ≥37,8°C persistente
- [ ] Disúria com calafrios
- [ ] Diminuição importante ou ausência de movimentação fetal (após 20 sem)
- [ ] Edema súbito e generalizado (face, mãos)
- [ ] Dispneia em repouso

**Maternidade de referência (vinculada via SISREG):** {maternidade_referencia}
**Telefone SAMU:** 192 | **Telefone unidade:** {telefone_unidade}

> **Suspeita de pré-eclâmpsia grave (cefaleia + escotomas + epigastralgia):** encaminhamento imediato ao PS obstétrico — risco de eclâmpsia e síndrome HELLP.

---

## 11. PUERPÉRIO

> **Definição:** período de 6 a 8 semanas após o parto, dividido em **imediato** (até 10 dias), **tardio** (10-45 dias) e **remoto** (>45 dias).
> **MS — Caderneta da Gestante:** mínimo 2 consultas no puerpério (1ª até 7 dias, 2ª até 42 dias).

### 11.1 Dados do parto

| Campo | Valor |
|---|---|
| Data e hora do parto | {data_parto} |
| Tipo de parto | {tipo_parto} *(vaginal espontâneo / vaginal com fórceps ou vácuo / cesárea eletiva / cesárea de urgência)* |
| Indicação (se cesárea) | {indicacao_cesarea} |
| IG no parto | {ig_parto} sem |
| Intercorrências intraparto | {intercorrencias_parto} |
| Apgar 1'/5'/10' | {apgar} |
| Peso e medidas RN | {dados_rn} |
| Aleitamento iniciado na 1ª hora? | {aleitamento_1h} |

### 11.2 1ª consulta puerperal (até 7 dias)

| Campo | Valor |
|---|---|
| Data | {data_puerpera_1} |
| Estado geral / mucosas | {estado_geral_1} |
| Pressão arterial | {pa_puerpera_1} |
| Involução uterina | {involucao_uterina} *(adequada / atrasada)* |
| Loquiação | {loquios} *(rubra / fusca / alba / fétida — investigar)* |
| Mamas (ingurgitamento, fissuras, mastite) | {mamas_1} |
| Períneo / cicatriz cesárea | {ferida_operatoria} |
| Aleitamento materno | {aleitamento_1} *(exclusivo / complementado / não / dificuldades)* |
| Triagem para depressão pós-parto (EPDS) | {epds_score_1} *(≥10 = rastreamento positivo, encaminhar)* |
| Triagem para violência doméstica | {triagem_violencia_1} |
| Métodos contraceptivos discutidos | {contracepcao_pos_parto_1} |

### 11.3 2ª consulta puerperal (até 42 dias)

| Campo | Valor |
|---|---|
| Data | {data_puerpera_2} |
| Estado geral | {estado_geral_2} |
| Pressão arterial | {pa_puerpera_2} |
| Retorno menstrual? | {retorno_menstrual} |
| Aleitamento materno | {aleitamento_2} |
| EPDS reaplicada | {epds_score_2} |
| Citologia / exames pendentes recuperados? | {exames_recuperados} |
| Método contraceptivo iniciado | {metodo_contraceptivo} |
| Imunizações pós-parto (rubéola se susceptível, dTpa se não tomou na gestação) | {imunizacoes_pos_parto} |

### 11.4 Orientações no puerpério

- [ ] Aleitamento materno exclusivo até 6 meses, complementado até 2 anos (MS/OMS)
- [ ] Sinais de alarme puerperais: febre, sangramento aumentado/fétido, dor mamária com hiperemia, dispneia, dor torácica, sinais de TVP em MMII, cefaleia intensa, alterações de humor extremas (ideação suicida, desconexão com o RN)
- [ ] Retorno sexual após involução uterina e cessação dos lóquios (~30-40 dias); contracepção iniciada antes do retorno
- [ ] Cuidados com RN orientados: posição supina para dormir, vacinação na maternidade (BCG, Hep B) e UBS, agendamento da 1ª consulta pediátrica em até 7 dias
- [ ] Encaminhamento à puericultura: {puericultura_unidade}

> ⚠️ **Depressão pós-parto:** EPDS ≥10 indica rastreamento positivo. Encaminhar para avaliação psiquiátrica/psicológica via CAPS-AD ou matriciamento em saúde mental. Ideação suicida ou sintomas psicóticos = emergência psiquiátrica.

---

## 12. Identificação do profissional responsável

| Campo | Valor |
|---|---|
| Profissional | {profissional_nome} |
| Categoria | {categoria_profissional} *(médico / enfermeiro obstetra / obstetriz)* |
| Conselho de classe | {conselho_classe} |
| Número do registro | {registro_profissional} |
| Data | {data_registro} |
| Assinatura | ________________________ |

---

> ⚠️ **Esta caderneta acompanha a gestante em todos os atendimentos.** Deve ser apresentada na maternidade no momento do parto e nas consultas de puericultura do bebê.
>
> ⚠️ **Direitos da gestante (Lei 11.108/2005 e Lei 11.634/2007):** acompanhante durante todo o trabalho de parto, parto e pós-parto; vinculação prévia à maternidade de referência via SISREG.
>
> ⚠️ **Este registro não substitui prontuário hospitalar.** É documento de comunicação entre níveis de atenção (UBS ↔ maternidade ↔ puericultura) e instrumento de empoderamento da gestante.
