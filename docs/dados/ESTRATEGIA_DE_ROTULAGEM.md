# Estratégia de Rotulagem

**Agente responsável:** `DataEngineeringAgent`
**Status:** Especificação aprovada — gerador **ainda não implementado**

---

## 1. O problema que esta estratégia precisa resolver

Gerar rótulos sintéticos é fácil. Gerar rótulos sintéticos **honestos** é difícil, e há uma
armadilha específica que precisa ser evitada.

**A armadilha:** se o rótulo for produzido pela mesma regra determinística que o modelo depois vai
receber como feature, o experimento é circular. Um Random Forest recupera uma regra booleana
`OR` de sete condições com F1 ≈ 1,00 em poucas centenas de amostras. O resultado seria uma tabela
de métricas bonita e completamente vazia de significado — e, pior, seria fácil apresentá-la como
se demonstrasse alguma coisa.

Concretamente, seria circular fazer isto:

```python
# ANTI-PADRÃO — NÃO FAZER
alto_risco = (idade > 35) or has_cronica or diabetes_previo or gemelaridade  # etc.
```

Isso é literalmente `CRITERIOS_ALTO_RISCO` de `lib/workflows/obstetrico.py:50-66`. Se ela gerasse
os rótulos, o "baseline determinístico" descrito em `docs/ml/DEFINICAO_DO_PROBLEMA.md` §4 acertaria
100 % e os modelos de ML não teriam nada a superar.

---

## 2. A estratégia adotada: modelo latente logístico com ruído

O rótulo é gerado por um **processo probabilístico em três camadas**, não por uma regra booleana.

### Camada 1 — Escore latente linear

Para cada registro, calcula-se um escore latente contínuo:

```
z = β₀ + Σᵢ βᵢ · xᵢ
```

Os coeficientes `βᵢ` são fixos, versionados no código e **escolhidos para refletir a direção e a
magnitude relativa** dos fatores de risco descritos nos protocolos MS/FEBRASGO. Eles **não foram
estimados a partir de dados reais** — são parâmetros de plausibilidade clínica, e essa distinção é
registrada aqui e no relatório técnico.

| Variável | β | Direção | Racional clínico |
|---|---|---|---|
| intercepto `β₀` | −3,10 | — | Calibra a prevalência para ≈ 22 % |
| `has_cronica` | +1,60 | ↑ | Hipertensão crônica é fator maior |
| `diabetes_previo` | +1,45 | ↑ | DM prévio é fator maior |
| `pre_eclampsia_previa` | +1,70 | ↑ | Recorrência é o preditor isolado mais forte |
| `cardiopatia` | +1,90 | ↑ | Fator maior, baixa prevalência |
| `nefropatia` | +1,75 | ↑ | Fator maior |
| `gemelaridade` | +1,30 | ↑ | Gestação múltipla |
| `tev_previo` | +1,20 | ↑ | Trombofilia/TEV |
| `natimorto_previo` | +1,10 | ↑ | Antecedente obstétrico desfavorável |
| `(pas−120)/10` | +0,38 | ↑ | Contínuo, não dicotomizado |
| `(pad−75)/10` | +0,32 | ↑ | Contínuo |
| `(imc−24)/5` | +0,34 | ↑ | Contínuo |
| `idade < 16` | +1,15 | ↑ | Extremo inferior |
| `(idade−28)/10` para idade ≥ 28 | +0,40 | ↑ | Crescente após 28 |
| `abortos ≥ 2` | +0,75 | ↑ | Abortamento de repetição |
| `cesareas_previas ≥ 2` | +0,60 | ↑ | |
| `infeccao_sexual_ativa` | +0,85 | ↑ | HIV/sífilis/hepatite |
| `tabagismo` | +0,45 | ↑ | |
| `proteinuria ≥ 1+` | +0,95 | ↑ | Ordinal codificado |
| `hemoglobina < 11` | +0,50 | ↑ | Anemia |
| `glicemia_jejum ≥ 92` | +0,55 | ↑ | Rastreio DMG |
| `intervalo_interpartal < 18 meses` | +0,40 | ↑ | |
| `escolaridade_anos` | −0,04 | ↓ | Proxy socioeconômico fraco |

### Camada 2 — Interações não-lineares

Três termos de interação, que existem para **dar ao Random Forest algo que a Regressão Logística
não captura sem engenharia manual**. Sem eles, os dois modelos empatariam e a comparação seria
estéril.

| Interação | β | Racional |
|---|---|---|
| `idade ≥ 35` × `has_cronica` | +0,80 | Risco combinado superaditivo |
| `imc ≥ 30` × `diabetes_previo` | +0,70 | Obesidade agrava disglicemia |
| `gemelaridade` × `(pas−120)/10` | +0,45 | Múltipla com pressão elevada |

### Camada 3 — Amostragem estocástica

```
p = σ(z)                      # sigmoide → probabilidade latente, salva como `risco_latente`
alto_risco ~ Bernoulli(p)     # rótulo final é AMOSTRADO, não limiarizado
```

A amostragem de Bernoulli é a decisão mais importante desta estratégia. Ela introduz **erro de
Bayes irredutível**: mesmo o processo gerador, conhecendo `p` exatamente, não consegue prever o
rótulo com certeza. Consequências:

- Nenhum modelo pode atingir ROC-AUC = 1,00. O teto teórico é calculável e será reportado.
- As comparações entre modelos passam a ser informativas, porque há espaço real entre eles.
- As probabilidades previstas podem ser avaliadas quanto à **calibração** contra `risco_latente`.

Se usássemos `alto_risco = (p > 0.5)`, voltaríamos à armadilha da camada determinística, apenas com
uma fronteira mais complicada.

---

## 3. Por que isso não é circular

| Aspecto | Gerador de rótulos | Baseline determinístico (`CRITERIOS_ALTO_RISCO`) |
|---|---|---|
| Forma | Logística contínua com interações | Disjunção booleana |
| Variáveis contínuas | Usadas como contínuas (PA, IMC, idade) | Dicotomizadas por corte (`>35a`, `IMC≥35`) |
| Interações | Três termos explícitos | Nenhuma |
| Estocasticidade | Bernoulli | Determinístico |
| Pesos | Diferenciados por fator | Todos iguais (qualquer critério basta) |

São processos estruturalmente diferentes. O baseline determinístico terá **alto recall e baixa
precisão** (dispara com qualquer critério isolado) — exatamente o padrão que se espera de uma regra
`OR` ampla, e exatamente o problema clínico que motiva usar ML: encaminhar ao pré-natal de alto
risco toda gestante com um único fator leve sobrecarrega o serviço.

**A hipótese que o experimento testa:** os modelos de ML conseguem manter o recall do baseline
determinístico enquanto melhoram substancialmente a precisão. Essa hipótese pode falhar, e se
falhar será reportada como falha.

---

## 4. Ausências e ruído de medição

Dados clínicos reais não vêm completos. O gerador injeta ausências com dois mecanismos distintos,
para que o pipeline de imputação e o caminho de dados incompletos sejam exercitados de verdade.

| Variável | Mecanismo | Taxa | Racional |
|---|---|---|---|
| `hemoglobina_g_dl` | MCAR | 12 % | Exame não colhido, ao acaso |
| `glicemia_jejum_mg_dl` | MCAR | 15 % | Idem |
| `proteinuria_fita` | **MAR** — ausência depende de `ig_semanas < 20` | 30 % no 1º trimestre, 5 % depois | Fita de proteinúria é rotina a partir do 2º trimestre |
| `escolaridade_anos` | MCAR | 20 % | Campo administrativo frequentemente vazio |
| `intervalo_interpartal_meses` | **Estrutural** | 100 % em nulíparas | Não é ausência: não se aplica |

A distinção entre ausência estrutural (`partos == 0`) e ausência por não-coleta é preservada: a
primeira recebe um indicador `nao_aplicavel`, a segunda entra na imputação. Tratar as duas do mesmo
jeito ensinaria ao modelo que "nulípara" e "dado perdido" são a mesma coisa.

Além disso, `pas_mmhg` e `pad_mmhg` recebem ruído gaussiano `N(0, 4)` arredondado, simulando
variabilidade de aferição.

---

## 5. Reprodutibilidade

| Controle | Implementação |
|---|---|
| Semente única | `numpy.random.default_rng(42)`, propagada a todas as amostragens |
| Sem dependência de ordem | Cada registro é gerado a partir do seu índice; paralelizável sem mudar resultado |
| Manifesto com hash | SHA-256 do Parquet gravado em `artifacts/data/*.manifest.json`, versionado no git |
| Verificação | `python scripts/train.py --verificar-dataset` regenera e compara o hash; diverge ⇒ falha |
| Teste automatizado | `tests/unit/test_dataset_reprodutivel.py` gera duas vezes e compara igualdade |

---

## 6. Limitações desta estratégia

Declaradas aqui porque o ponto do documento é ser auditável, não convincente.

1. **A estrutura de dependência é a que nós escolhemos.** Os modelos aprendem relações que
   inserimos deliberadamente. Isso valida o *pipeline*, não a *hipótese clínica*.
2. **As correlações entre features são simplificadas.** IMC e diabetes são gerados com correlação
   moderada imposta; no mundo real a rede de dependências é muito mais densa.
3. **Não há viés de seleção, de aferição, nem efeito de centro.** Dados reais de pré-natal têm
   todos os três, e são as principais causas de queda de desempenho na implantação.
4. **A prevalência de 22 % é uma escolha de projeto**, não uma medida epidemiológica brasileira.
5. **Um modelo com excelente desempenho aqui pode ter desempenho arbitrariamente ruim em dados
   reais.** Não há como estimar quanto, a partir deste experimento.

O uso legítimo destes dados é: demonstrar que o pipeline de ML — validação, treino, comparação,
explicabilidade, integração, auditoria — está construído corretamente. Nada além disso deve ser
afirmado, na documentação, na interface ou na apresentação.
