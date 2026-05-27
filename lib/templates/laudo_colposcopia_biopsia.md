# LAUDO DE COLPOSCOPIA E BIÓPSIA DE COLO UTERINO

**Instituição:** {instituicao}
**CNES:** {cnes}
**Data do exame:** {data_exame}
**Médico solicitante:** {medico_solicitante} — CRM {crm_solicitante}

---

## 1. Identificação da paciente

| Campo | Valor |
|---|---|
| Nome | {paciente_nome} |
| Data de nascimento | {paciente_dn} ({paciente_idade} anos) |
| ID interno / SUS Card | {paciente_id} |
| Gestações / Paridade (GPA) | {gpa} |
| DUM | {dum} |
| Status menopausa | {status_menopausa} |
| Uso atual de contraceptivo hormonal / TRH | {uso_hormonal} |

## 2. Indicação clínica

{indicacao_clinica}

> Indicações típicas (Diretrizes INCA 2016 — Rastreamento do Câncer do Colo do Útero):
> - Citologia (Papanicolau) alterada: ASC-US persistente, ASC-H, LSIL ≥25a, HSIL, AGC, AIS, carcinoma
> - Teste de HPV-AR positivo com citologia reflexa alterada
> - Inspeção visual suspeita (colo friável, lesão exofítica, sangramento ao toque)
> - Seguimento pós-tratamento de NIC (CAF/conização)

## 3. Achados pré-colposcópicos

| Campo | Valor |
|---|---|
| Inspeção da vulva e períneo | {inspecao_vulva} |
| Espéculo — paredes vaginais | {paredes_vaginais} |
| Colo uterino — aspecto macroscópico | {aspecto_colo} |
| Corrimento / secreção | {corrimento} |
| Sangramento ao contato | {sangramento_contato} |

## 4. Colposcopia — Nomenclatura IFCPC 2011 (Rio de Janeiro)

### 4.1 Avaliação geral

| Aspecto | Resultado |
|---|---|
| Colposcopia adequada? | {colposcopia_adequada} *(sim / não — justificar: sangramento, inflamação, cicatriz)* |
| Junção escamocolunar (JEC) visível? | {jec_visivel} *(completamente / parcialmente / não visível)* |
| Zona de transformação (ZT) | {zt_tipo} *(tipo 1: ectocervical / tipo 2: endocervical visível / tipo 3: endocervical não visível)* |

### 4.2 Achados após ácido acético 5%

| Achado | Localização (quadrante) | Extensão | Grau |
|---|---|---|---|
| Epitélio acetobranco | {acetobranco_local} | {acetobranco_extensao} | {acetobranco_grau} *(fino = G1 / denso = G2)* |
| Mosaico | {mosaico_local} | {mosaico_extensao} | {mosaico_grau} *(fino = G1 / grosseiro = G2)* |
| Pontilhado | {pontilhado_local} | {pontilhado_extensao} | {pontilhado_grau} *(fino = G1 / grosseiro = G2)* |
| Vasos atípicos | {vasos_atipicos} | — | suspeita de invasão |
| Orifícios glandulares espessados | {orificios_espessados} | — | — |
| Iodo (teste de Schiller) | {schiller} *(iodo-positivo normal / iodo-negativo = suspeito)* | — | — |

### 4.3 Achados sugestivos de invasão

- [ ] Superfície irregular, erosão ou ulceração
- [ ] Vasos atípicos
- [ ] Lesão exofítica friável
- [ ] Necrose

{achados_invasao_detalhes}

## 5. Conclusão colposcópica

**Impressão colposcópica:** {impressao_colposcopica}

> Categorias possíveis (IFCPC 2011):
> - **Normal** (epitélio escamoso original, ectopia, ZT normal, iodo-positiva)
> - **Achados anormais menores (G1)** — sugestivos de LSIL / NIC 1
> - **Achados anormais maiores (G2)** — sugestivos de HSIL / NIC 2-3
> - **Suspeita de invasão**
> - **Miscelânea** (condilomatose, leucoplasia, erosão, inflamação, pólipo, endometriose)

## 6. Procedimentos realizados na mesma sessão

- [ ] Biópsia dirigida do colo — local: {biopsia_local}, número de fragmentos: {biopsia_fragmentos}
- [ ] Curetagem endocervical (CEC) — justificativa: {cec_justificativa}
- [ ] Vulvoscopia complementar
- [ ] Outros: {outros_procedimentos}

**Material enviado para histopatológico:** {material_enviado}
**Laboratório de destino:** {laboratorio_anatomia_patologica}

---

## 7. LAUDO HISTOPATOLÓGICO (preencher após retorno do AP)

| Campo | Valor |
|---|---|
| Nº do exame AP | {numero_ap} |
| Data de coleta | {data_coleta_ap} |
| Data de liberação | {data_liberacao_ap} |
| Material recebido | {material_descricao} |

### 7.1 Macroscopia

{macroscopia}

### 7.2 Microscopia

{microscopia}

### 7.3 Diagnóstico anatomopatológico

**Diagnóstico:** {diagnostico_ap}

> Categorias mais frequentes:
> - Cervicite crônica inespecífica
> - Metaplasia escamosa imatura/madura
> - **NIC 1 / LSIL** — Lesão Intraepitelial de Baixo Grau
> - **NIC 2 / HSIL** — Lesão Intraepitelial de Alto Grau (p16 positivo)
> - **NIC 3 / HSIL** — Lesão Intraepitelial de Alto Grau com extensão total
> - **AIS** — Adenocarcinoma in situ
> - **Carcinoma escamoso microinvasor** (≤5mm profundidade)
> - **Carcinoma escamoso invasor**
> - **Adenocarcinoma invasor**

### 7.4 Imunohistoquímica complementar (quando indicada)

| Marcador | Resultado |
|---|---|
| p16 | {p16} *(positivo difuso = HSIL provável / negativo ou focal = LSIL provável)* |
| Ki-67 | {ki67} |
| HPV in situ | {hpv_in_situ} |

## 8. Conduta sugerida (Diretrizes INCA 2016)

{conduta_sugerida}

> **Resumo de conduta por diagnóstico:**
> - **LSIL / NIC 1:** seguimento citológico + colposcópico em 6 meses (≥25a); em <25a, citologia anual por 3 anos
> - **HSIL / NIC 2-3:** excisão da ZT (CAF/conização) — em adolescentes/gestantes, individualizar
> - **AIS:** conização diagnóstica + histerectomia simples se prole completa
> - **Carcinoma microinvasor (≤3mm, sem invasão linfovascular):** conização pode ser suficiente em mulher com desejo reprodutivo
> - **Carcinoma invasor:** estadiamento FIGO + encaminhamento oncologia ginecológica

## 9. Recomendações à paciente

{recomendacoes_paciente}

- [ ] Abstinência sexual e absorvente interno por {dias_abstinencia} dias após biópsia
- [ ] Retorno em {prazo_retorno} para entrega do resultado e definição de conduta
- [ ] Sinais de alarme orientados: sangramento aumentado, febre, dor pélvica intensa, secreção fétida
- [ ] Esquema vacinal HPV revisado? {vacina_hpv_status}

---

**Médico colposcopista:** {colposcopista_nome}
**CRM:** {colposcopista_crm}
**RQE Ginecologia/Mastologia:** {colposcopista_rqe}

**Médico patologista:** {patologista_nome}
**CRM:** {patologista_crm}

**Data do laudo:** {data_laudo}

_Documento assinado digitalmente conforme MP 2.200-2/2001 (ICP-Brasil)._

---

> ⚠️ **Limitações inerentes ao método:** colposcopia tem acurácia diagnóstica dependente da visualização adequada da ZT. Em ZT tipo 3 (endocervical não visível), o risco de subestimar lesão glandular é maior — considerar curetagem endocervical e/ou conização diagnóstica.
>
> ⚠️ **Discrepância citologia/colposcopia/AP:** quando houver discordância de dois graus entre os métodos (ex.: HSIL na citologia + colposcopia normal + AP benigno), reavaliar em comissão multidisciplinar antes de excluir lesão.
>
> ⚠️ **Este laudo não substitui correlação clínica.** A conduta final deve ser definida pelo médico assistente integrando este exame, citologia prévia, histórico e desejo reprodutivo da paciente.
