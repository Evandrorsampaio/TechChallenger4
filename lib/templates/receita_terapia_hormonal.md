# RECEITUÁRIO MÉDICO

**Instituição:** {instituicao}
**Endereço:** {endereco_instituicao}
**CNES:** {cnes}

---

## Identificação da paciente

| Campo | Valor |
|---|---|
| Nome | {paciente_nome} |
| Data de nascimento | {paciente_dn} ({paciente_idade} anos) |
| CPF | {paciente_cpf} |
| Cartão SUS / Convênio | {paciente_convenio} |

## Identificação do prescritor

| Campo | Valor |
|---|---|
| Médico | {medico_nome} |
| CRM | {medico_crm} |
| Especialidade / RQE | {medico_rqe} |
| Data | {data_prescricao} |

---

## Prescrição

### {medicamento_principio_ativo} ({medicamento_comercial})

**Apresentação:** {apresentacao}
**Quantidade:** {quantidade}

**Posologia:**
{posologia}

> Exemplos típicos por classe:
> - **COC (etinilestradiol + drospirenona 0,02/3 mg):** 1 comprimido VO/dia, sempre no mesmo horário, por 24 dias consecutivos seguidos de 4 dias de pausa (ou placebo). Início no 1º dia da menstruação.
> - **POP (desogestrel 75 mcg):** 1 comprimido VO/dia, continuamente, sem pausa, sempre no mesmo horário (tolerância de atraso ≤12h).
> - **DIU hormonal (levonorgestrel 52 mg):** dispositivo intrauterino com inserção em até 7 dias do início do ciclo. Duração 5 anos (Mirena) ou 3 anos (Kyleena).
> - **TRH transdérmica (estradiol 50 mcg/24h):** 1 adesivo a cada 3-4 dias, em região glútea ou abdominal.

**Duração do tratamento:** {duracao}

**Orientações à paciente:**
{orientacoes}

---

## Considerações clínicas obrigatórias (checklist do prescritor)

- [ ] Confirmada ausência de contraindicações absolutas para a categoria:
  - **Estrogênio:** tabagismo + idade ≥35a, HAS não controlada, TEV/TEP prévio, enxaqueca com aura, hepatopatia ativa, câncer hormônio-dependente
  - **Progestágeno:** sangramento vaginal sem causa esclarecida, câncer de mama atual
- [ ] Aferição de pressão arterial: {pa}
- [ ] IMC: {imc}
- [ ] Anamnese de risco cardiovascular e tromboembólico realizada
- [ ] Paciente orientada sobre efeitos adversos esperados (sangramento de escape nos 3 primeiros ciclos, mastalgia, cefaleia, alteração de humor)
- [ ] Paciente orientada sobre sinais de alarme que motivam suspensão imediata:
  - Dor torácica intensa, dispneia súbita (suspeita de TEP)
  - Dor em panturrilha unilateral (suspeita de TVP)
  - Cefaleia intensa, alterações visuais, déficit neurológico focal
  - Icterícia, dor em hipocôndrio direito
- [ ] Retorno em {prazo_retorno} para reavaliação de tolerância e efetividade

---

## Categoria de risco

| Aspecto | Classificação |
|---|---|
| Categoria gestacional (FDA) | {categoria_gestacao} |
| Compatibilidade com lactação | {categoria_lactacao} |
| Critério MEC OMS (elegibilidade contraceptiva) | {mec_oms_categoria} |

> **MEC OMS (Medical Eligibility Criteria):**
> - **Categoria 1:** Sem restrição
> - **Categoria 2:** Vantagens geralmente superam riscos
> - **Categoria 3:** Riscos geralmente superam vantagens (uso desencorajado)
> - **Categoria 4:** Risco inaceitável (contraindicado)

---

**Assinatura e carimbo:** ________________________
**Data:** {data_prescricao}

_Receituário emitido eletronicamente conforme RDC ANVISA 471/2021 (validade 30 dias para medicamentos sob prescrição comum, ou conforme legislação específica para controlados)._

---

> ⚠️ **Esta receita é gerada por modelo e EXIGE revisão + assinatura de médico habilitado antes da entrega à paciente.** O assistente clínico atua como ferramenta de apoio à prescrição, nunca substitui a decisão e responsabilidade do prescritor.
