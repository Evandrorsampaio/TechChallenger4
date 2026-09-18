# Política Anti-Alucinação

**Agente responsável:** `LLMIntegrationAgent`
**Status:** Especificação — **nada implementado**. `lib/validacao.py` não existe; o validador
determinístico continua em `referencias/`, fora do pacote.
**Vinculado a:** ADR-007 (contrato somente-leitura) · ADR-010 (promoção do validador) ·
`CONTRATO_ENTRADA_SAIDA_LLM.md` · `CONTRATOS_DE_COMPONENTES.md` §5

---

> ### Banner de estado
> Nenhuma verificação foi executada. **Não existe taxa de rejeição medida** neste projeto. As
> tabelas de resultado da §6 estão vazias por decisão, e serão preenchidas exclusivamente com saída
> de `scripts/run_demo.py` e da suíte `tests/`. Qualquer número que apareça aqui sem essa origem é
> defeito do documento.

---

## 1. A ameaça, dita com precisão

O risco não é abstrato. Ele tem três componentes documentados neste repositório:

1. **O modelo é pequeno e repetitivo.** `lib/llm.py:84-88` registra que ~60 % das respostas do
   adapter da run 0217 apresentavam loops degenerativos, mitigados — não eliminados — por
   `repetition_penalty=1.2` e `no_repeat_ngram_size=4`.
2. **O sistema passará a manipular números clínicos.** Hoje o LLM não vê probabilidade nenhuma;
   com a camada de ML, ele recebe `0.75`, `0.31` e contribuições com sinal. Um modelo que inventa
   texto passa a poder inventar número, e número com aparência de saída de modelo é
   qualitativamente pior que texto vago: ele carrega autoridade que não tem.
3. **O consumidor é um profissional sob pressão de tempo.** A resposta será lida rápido. Um número
   errado não será auditado pelo leitor.

Portanto a política não é "melhorar o prompt". É **impedir estruturalmente que um número inventado
chegue à tela**, aceitando como custo que respostas legítimas também sejam descartadas.

### 1.1 O princípio que organiza tudo

> Prompt é pedido. Verificação é controle. **Só o controle entra no caminho crítico.**

Nenhuma camada desta política depende de o modelo cooperar.

---

## 2. As cinco camadas de defesa

| # | Camada | Natureza | Momento | Bloqueia? | Custo |
|---|---|---|---|---|---|
| 1 | Prompt estruturado com números permitidos | Preventiva | antes da geração | não | zero |
| 2 | Verificação numérica pós-geração | Detectiva | depois da geração | **sim** | regex, µs |
| 3 | Coerência de rótulo | Detectiva | depois da geração | **sim** | regex, µs |
| 4 | `ValidadorDeterministico` (5 regras promovidas) | Detectiva | depois da geração | **3 de 5** bloqueiam | regex, µs |
| 5 | Descarte + resposta estruturada | Corretiva | na entrega | — | render determinístico |

As camadas 2, 3 e 4 rodam **em paralelo lógico** sobre o mesmo texto e seus resultados são
combinados num único `ResultadoVerificacao`. Não há curto-circuito: mesmo que a camada 2 já tenha
reprovado, as demais rodam, porque o registro completo dos motivos alimenta a análise de erros.

---

## 3. Camada 1 — prompt estruturado

Detalhada em `PROMPTS_DE_EXPLICACAO.md`. O que importa aqui é o mecanismo específico:
**o prompt entrega uma lista fechada de numerais permitidos** (`{numeros_permitidos}`) e instrui o
modelo a reescrever a frase sem número quando precisar de um que não esteja na lista.

Isso muda a natureza do pedido. "Não invente números" é uma proibição abstrata que um modelo de 3B
não sabe verificar. "Use apenas estes: 0.31; 0.75; 75.0" é uma restrição concreta e local.

**Esta camada não bloqueia nada.** Ela existe para reduzir a taxa de descarte, que é o principal
risco prático da política. Se a taxa medida na §6 for alta, é esta camada que se ajusta — nunca a
camada 2.

---

## 4. Camada 2 — verificação numérica pós-geração

### 4.1 Definição de "numeral"

Extraem-se do texto gerado todas as ocorrências do padrão:

```
(?<![\w.])[-+]?\d{1,3}(?:[.,]\d+)?%?(?![\w])
```

Com três normalizações antes da comparação:

| Normalização | Motivo |
|---|---|
| Vírgula decimal → ponto (`0,75` → `0.75`) | Português brasileiro escreve com vírgula; o payload é JSON |
| Sufixo `%` removido e o valor mantido (`75%` → `75`) | `75` precisa casar com o derivado `prob_pct = 75.0` |
| Zeros à direita desprezados na comparação (`0.750` ≡ `0.75`) | Comparação é numérica, não textual |

### 4.2 Conjunto de números justificados

Construído por `llm_contract.numeros_justificados(payload)`. Contém:

| Origem | Itens |
|---|---|
| Payload direto | `threshold`; cada valor de `probabilities`; cada `contribution` de `top_features`; cada `value` numérico de `top_features` |
| Derivados pré-computados (`CONTRATO_ENTRADA_SAIDA_LLM.md` §5.3) | `prob_pct`; distância ao limiar |
| Constantes de domínio | os inteiros que aparecem nos `trecho` de `retrieved_sources` — ver §4.4 |
| Numerais estruturais | `1`, `2`, `3`, `4`, `5` quando usados como marcadores de lista |

### 4.3 Tolerância

Comparação por valor absoluto, com `tolerancia = 0.005` (`CONTRATOS_DE_COMPONENTES.md` §5). Um
numeral do texto é justificado se existir `v` no conjunto tal que `abs(n - v) <= tolerancia` **ou**
`abs(n - v*100) <= tolerancia` (para cobrir a forma percentual sem duplicar o conjunto).

`0.005` cobre arredondamento a duas casas decimais, que é a forma em que os números aparecerão. Não
cobre `0.75 → 0.8`, e isso é intencional: arredondar 75 % para 80 % é distorção clínica, não
formatação.

**Regra de governança:** a tolerância é constante do módulo, não parâmetro de chamada. Afrouxá-la
para reduzir a taxa de descarte é violação explícita da ADR-007.

### 4.4 O problema dos números dentro do `trecho` do protocolo

Um trecho de protocolo contém doses, semanas de gestação e percentuais legítimos: "TOTG 75 g entre
24 e 28 semanas". Se o LLM citar `75 g` corretamente, e `75` não estiver no conjunto justificado, o
texto é descartado por uma citação **correta**. Esse é um falso positivo do verificador, e ele é
frequente o bastante para exigir tratamento.

Duas opções foram consideradas:

| Opção | Efeito |
|---|---|
| **A** — incluir no conjunto justificado todos os numerais presentes nos `trecho` recuperados | Reduz falso positivo; amplia o conjunto permitido, o que reduz a força da camada |
| **B** — exigir que números de protocolo apareçam sempre acompanhados de unidade e fonte | Mantém o conjunto estreito; aumenta muito a taxa de descarte com um 3B |

**Decisão: opção A**, com uma qualificação que preserva a força da camada: os numerais vindos de
`trecho` entram num **subconjunto separado**, e o `ResultadoVerificacao` registra quantos numerais
do texto foram justificados por essa via. Se um texto justificar seu número de probabilidade por
coincidência com um número de protocolo, isso fica visível no rastro em vez de passar
silenciosamente.

O trade-off é declarado: a camada 2 é mais forte para números de modelo (que são poucos e
específicos) do que para números de conduta clínica (que são muitos e genéricos). Números de
modelo são o que a ADR-007 protege.

---

## 5. Camada 3 — coerência de rótulo

O texto não pode afirmar classificação diferente de `prediction`.

### 5.1 Léxico

| Rótulo | Termos afirmativos | Termos contraditórios |
|---|---|---|
| `alto_risco` | `alto risco`, `alto_risco`, `pré-natal de alto risco`, `risco elevado` | `risco habitual`, `habitual`, `baixo risco`, `risco usual`, `gestação de risco habitual` |
| `habitual` | `risco habitual`, `habitual`, `pré-natal de risco habitual` | `alto risco`, `alto_risco`, `risco elevado`, `pré-natal de alto risco` |

### 5.2 Regra

1. Se nenhum termo afirmativo do rótulo predito aparecer no texto → **reprova** (o texto não
   comunicou a estratificação, que é sua função primária).
2. Se algum termo contraditório aparecer **fora** de uma negação explícita → **reprova**.

Negação explícita = o termo contraditório é precedido, na mesma frase, por `não`, `não é`,
`descartado`, `afasta`, `em vez de`. Exemplo aceitável: *"Classificação alto risco; não se trata de
risco habitual."*

### 5.3 Casos especiais por modo

| Modo | Regra |
|---|---|
| `incompleto` | **Nenhum** termo de rótulo pode aparecer fora de negação. Regra invertida: presença de rótulo é que reprova (`PROMPTS_DE_EXPLICACAO.md` §6.3) |
| `bypass_regra` | O rótulo é o da regra; termos de probabilidade (`probabilidade`, `%`, `limiar`) reprovam |
| `degradado` | O rótulo é o da regra; o texto precisa conter `degradado` ou `indisponível` na primeira seção |

---

## 6. Camada 4 — as cinco regras do validador promovido

Origem: `referencias/validador_resposta_llm.py::ValidadorDeterministico`. O código existe, tem 6
casos de teste que passam no `__main__`, e é promovido para `lib/validacao.py` pela ADR-010
**sem reescrita da lógica**.

| # | Regra | Padrões | Classe | Bloqueia? |
|---|---|---|---|---|
| 1 | Diagnóstico definitivo | `PADROES_DIAGNOSTICO` (4 regex) | violação | **sim** |
| 2 | Posologia sem referência a protocolo | `PADROES_PRESCRICAO` (4 regex) sem `tem_disclaimer` | violação | **sim** |
| 3 | Categoria sensível sem serviço da rede | `CATEGORIAS_SENSITIVE` × `SERVICOS_REDE` | violação | **sim** |
| 4 | Ausência de citação de fonte | ausência de `fontes` e de menção textual | aviso | não |
| 5 | Linguagem dirigida à paciente | `PADROES_DIRIGIDO_PACIENTE` (5 regex) | aviso | não |

### 6.1 O que muda na promoção

Nada na lógica. Três coisas no entorno:

1. **Localização.** `referencias/validador_resposta_llm.py` → `lib/validacao.py`. O arquivo
   original **permanece**, com nota de depreciação, porque os relatórios da Fase 3 o referenciam
   por caminho (ADR-010, consequências).
2. **Os 6 casos do `__main__` viram testes.** `tests/unit/test_validacao_deterministica.py`
   reproduz os 6 asserts existentes, que passam a rodar em CI em vez de só quando alguém executa o
   arquivo à mão.
3. **Composição.** `verificar()` combina o `ResultadoValidacao` do validador com os resultados das
   camadas 2 e 3 num `ResultadoVerificacao` único.

### 6.2 Por que as regras 4 e 5 continuam sendo avisos

Endurecer a regra 4 (fonte) transformaria toda resposta sem RAG em descarte, inclusive as legítimas
do modo `incompleto`. Endurecer a regra 5 (tom) produziria descarte por falso positivo frequente:
`PADROES_DIRIGIDO_PACIENTE` casa com `fique calma`, que pode aparecer numa orientação sobre o que
*dizer* à paciente — uso correto.

Manter a semântica original é decisão deliberada, e o custo é declarado: **é possível que uma
resposta com tom inadequado chegue ao usuário**, marcada com aviso no rastro. A alternativa
produziria taxa de descarte pior sem ganho de segurança clínica.

### 6.3 O `ValidadorLLM` continua desligado

`referencias/validador_resposta_llm.py::ValidadorLLM` funciona, mas custa uma segunda chamada ao
modelo (5–10 s). A ADR-010 mantém a decisão original de não integrá-lo — com a correção de que essa
decisão vale para o `ValidadorLLM`, **não** para o `ValidadorDeterministico`, que custa
microssegundos e foi excluído por arrasto.

Ele fica disponível, desabilitado por padrão, atrás de flag `VALIDADOR_LLM_HABILITADO`, para uso
em avaliação offline — onde 10 s por amostra é aceitável e um segundo par de olhos tem valor.

---

## 7. Camada 5 — descarte e fallback

### 7.1 O que dispara descarte

Descarte ocorre se **qualquer** uma destas for verdadeira:

| Gatilho | Camada |
|---|---|
| Existe numeral no texto sem correspondente no conjunto justificado (tolerância 0,005) | 2 |
| Nenhum termo afirmativo do rótulo predito aparece no texto | 3 |
| Termo contraditório do rótulo aparece fora de negação | 3 |
| Modo `incompleto` e o texto contém termo de rótulo fora de negação | 3 |
| Modo `bypass_regra`/`degradado` e o texto menciona probabilidade ou limiar | 3 |
| Violação das regras 1, 2 ou 3 do validador | 4 |
| Seção obrigatória ausente (`### Estratificação`, `### Avisos`) | formato |
| Um dos dois avisos obrigatórios não aparece literalmente | formato |
| Texto vazio, ou < 80 caracteres | formato |
| Repetição degenerativa: um 8-grama aparece 3 ou mais vezes | formato |
| `chat_model.invoke` levantou exceção ou estourou timeout | execução |

### 7.2 O que NÃO dispara descarte

| Situação | Tratamento |
|---|---|
| Avisos das regras 4 e 5 do validador | Registrados no rastro; resposta entregue |
| `retrieved_sources` vazio com a frase de cobertura ausente presente | Correto. Entregue |
| Texto mais curto que o pedido, mas com todas as seções | Entregue |
| Numeral justificado apenas por coincidência com número de protocolo | Entregue, com contagem registrada (§4.4) |

### 7.3 O que o usuário vê quando há descarte

A resposta estruturada determinística (`llm_contract.resposta_estruturada(payload)`), precedida de
uma faixa:

```markdown
> ℹ️ **Síntese automática não aprovada na verificação.** O texto gerado pelo modelo de
> linguagem foi descartado porque {motivo_resumido}. Abaixo está o resultado
> estruturado, produzido diretamente pela camada de machine learning — os números
> são os mesmos, sem intermediação de texto gerado.
```

Três propriedades desse desenho:

**O usuário não perde informação.** A resposta estruturada contém rótulo, probabilidade, limiar,
fatores, fontes e avisos. O que se perde é a narrativa que amarra tudo — inconveniente, não
lacuna. Por isso `resposta_estruturada` é implementada **primeiro**
(`CONTRATO_ENTRADA_SAIDA_LLM.md` §10).

**O motivo é dito.** `{motivo_resumido}` é uma frase por classe de gatilho: "o texto continha um
número sem correspondência nos dados do modelo", "o texto contradisse a classificação", "o texto
não incluiu os avisos obrigatórios". O usuário não vê a regex; vê o motivo.

**A linguagem não é de erro.** "Não aprovada na verificação" e não "falha do sistema". Descarte é o
mecanismo funcionando (INV-4 do contrato). Chamá-lo de erro treinaria a equipe a ignorá-lo.

### 7.4 O que NÃO acontece no descarte

| Tentação | Por que é recusada |
|---|---|
| Pedir ao LLM que corrija e gerar de novo | +5–10 s; o novo texto também não é verificado a priori; e a ADR-010 já registra latência como critério de recusa |
| Remover o número órfão e entregar o resto | Se o modelo inventou um número, a confiança no resto caiu junto. Descarte é total |
| Entregar o texto com um aviso e deixar o profissional julgar | Transfere ao leitor a verificação que o sistema existe para fazer |
| Não registrar o descarte para não "poluir" a métrica | Viola INV-5 e o princípio de honestidade |

---

## 8. Algoritmo completo (pseudocódigo)

```python
# lib/validacao.py  — PROJETADO, NÃO IMPLEMENTADO

TOLERANCIA = 0.005          # constante do módulo; NÃO é parâmetro
MIN_CARACTERES = 80
NGRAMA_REPETICAO = 8
MAX_REPETICOES_NGRAMA = 2   # a 3ª ocorrência reprova


@dataclass(frozen=True)
class ResultadoVerificacao:
    aprovada: bool
    numeros_nao_justificados: list[str]
    numeros_justificados_por_protocolo: int   # visibilidade do trade-off §4.4
    contradicao_rotulo: bool
    rotulo_ausente: bool
    secoes_faltantes: list[str]
    avisos_obrigatorios_ausentes: list[str]
    repeticao_degenerativa: bool
    violacoes_clinicas: list[str]   # regras 1-3 do ValidadorDeterministico
    avisos: list[str]               # regras 4-5, não bloqueiam
    motivo_resumido: str            # exibido ao usuário quando aprovada=False


def verificar(texto, payload, modo, variante) -> ResultadoVerificacao:

    # ---------- formato ----------
    secoes_faltantes = secoes_obrigatorias(modo, variante) - secoes_presentes(texto)

    avisos_ausentes = [
        aviso for aviso in (payload['safety_notice'],
                            payload['aviso_dados_sinteticos'])
        if normalizar(aviso) not in normalizar(texto)
    ]

    texto_curto = len(texto.strip()) < MIN_CARACTERES

    repeticao = any(
        contagem > MAX_REPETICOES_NGRAMA
        for contagem in contar_ngramas(texto, NGRAMA_REPETICAO).values()
    )

    # ---------- camada 2: números ----------
    justificados_modelo   = numeros_justificados(payload)        # conjunto estreito
    justificados_protocolo = numeros_de_trechos(payload)         # conjunto amplo, §4.4

    orfaos, por_protocolo = [], 0
    for bruto in extrair_numerais(texto):
        n = normalizar_numeral(bruto)            # vírgula→ponto, remove %, float
        if casa(n, justificados_modelo, TOLERANCIA):
            continue
        if casa(n, justificados_protocolo, TOLERANCIA):
            por_protocolo += 1
            continue
        if eh_marcador_de_lista(bruto, texto):   # "1.", "2." no início da linha
            continue
        orfaos.append(bruto)

    # ---------- camada 3: rótulo ----------
    if modo == 'incompleto':
        # regra invertida: NENHUM rótulo pode aparecer
        contradicao = any(
            termo_fora_de_negacao(texto, t)
            for t in TODOS_OS_TERMOS_DE_ROTULO
        )
        rotulo_ausente = False
    else:
        afirmativos   = TERMOS_AFIRMATIVOS[payload['prediction']]
        contraditorios = TERMOS_CONTRADITORIOS[payload['prediction']]
        rotulo_ausente = not any(t in normalizar(texto) for t in afirmativos)
        contradicao = any(
            termo_fora_de_negacao(texto, t) for t in contraditorios
        )

    if modo in ('bypass_regra', 'degradado'):
        # nestes modos não existe probabilidade; mencioná-la é contradição
        contradicao = contradicao or menciona_probabilidade(texto)

    # ---------- camada 4: validador promovido ----------
    categoria = categoria_predominante(payload['retrieved_sources'])
    res_validador = ValidadorDeterministico().validar(
        resposta=texto,
        categoria=categoria,
        fontes=payload['retrieved_sources'],
    )

    # ---------- composição ----------
    reprovado_por = []
    if orfaos:                reprovado_por.append('numero_orfao')
    if contradicao:           reprovado_por.append('contradicao_rotulo')
    if rotulo_ausente:        reprovado_por.append('rotulo_ausente')
    if secoes_faltantes:      reprovado_por.append('secao_faltante')
    if avisos_ausentes:       reprovado_por.append('aviso_ausente')
    if texto_curto:           reprovado_por.append('texto_curto')
    if repeticao:             reprovado_por.append('repeticao')
    if res_validador.violacoes: reprovado_por.append('violacao_clinica')

    return ResultadoVerificacao(
        aprovada=not reprovado_por,
        numeros_nao_justificados=orfaos,
        numeros_justificados_por_protocolo=por_protocolo,
        contradicao_rotulo=contradicao,
        rotulo_ausente=rotulo_ausente,
        secoes_faltantes=sorted(secoes_faltantes),
        avisos_obrigatorios_ausentes=avisos_ausentes,
        repeticao_degenerativa=repeticao,
        violacoes_clinicas=res_validador.violacoes,
        avisos=res_validador.avisos,
        motivo_resumido=frase_de_motivo(reprovado_por),
    )
```

### 8.1 Integração no nó do workflow

```python
# lib/workflows/risco_ml.py::_sintetizar_com_llm + _validar_resposta_llm

def _sintetizar_com_llm(chat_model):
    def node(state):
        payload = state['payload_llm']
        try:
            texto = llm_contract.sintetizar(
                chat_model, payload, variante=state['variante_prompt'])
            falha = None
        except Exception as e:                      # ERR-LLM-02
            texto, falha = '', f'{type(e).__name__}: {e}'
        return {
            'texto_llm': texto,
            'falha_llm': falha,
            'raciocinio': state.get('raciocinio', []) + [
                'Síntese LLM gerada.' if not falha
                else f'Falha na geração ({falha}) — segue para resposta estruturada.'
            ],
        }
    return node


def _validar_resposta_llm(state):
    payload = state['payload_llm']
    if state.get('falha_llm'):
        ver = ResultadoVerificacao.reprovada_por_execucao(state['falha_llm'])
    else:
        ver = validacao.verificar(
            state['texto_llm'], payload,
            modo=state['modo'], variante=state['variante_prompt'])

    return {
        'verificacao': ver,
        'resposta_texto': (state['texto_llm'] if ver.aprovada
                           else llm_contract.resposta_estruturada(payload)),
        'texto_descartado': not ver.aprovada,
        'raciocinio': state.get('raciocinio', []) + [
            'Verificação anti-alucinação: APROVADA.' if ver.aprovada
            else f'Verificação anti-alucinação: DESCARTADA ({ver.motivo_resumido}).'
        ],
    }
```

**Duas propriedades a notar.** A verificação é um nó separado da geração, o que permite testá-la
sem LLM: o teste injeta texto e payload e verifica o resultado — é o que torna o catálogo de
`CASOS_DE_TESTE_LLM.md` executável em CPU, sem GPU e sem pesos. E falha de execução do modelo
entra pelo mesmo caminho de reprovação, em vez de ter tratamento próprio; uma só porta de saída.

---

## 9. Medição e reporte da taxa de rejeição

### 9.1 Definição

```
taxa_de_rejeicao = descartes / sinteses_tentadas
```

Contabilizada por execução do workflow que chegue ao nó `validar_resposta_llm`. Não inclui
execuções que nunca geraram (modo `incompleto` quando configurado sem LLM, perfil `ml-only`).

### 9.2 Onde fica registrada

| Destino | Conteúdo |
|---|---|
| Rastro (`state['raciocinio']`) | Uma linha por execução, com o motivo |
| Log estruturado (`lib/observabilidade.py`) | Evento `verificacao_llm` com todos os campos de `ResultadoVerificacao` |
| `predicoes_ml` | **Não.** A tabela registra a predição, não a verificação do texto. Modo continua `normal` |
| `artifacts/metrics/verificacao_llm.json` | Agregado produzido por `scripts/run_demo.py` |

A decisão de **não** acrescentar coluna a `predicoes_ml` preserva o DDL de
`ARQUITETURA_ALVO.md` §5.3 e mantém a separação: aquela tabela audita decisões clínicas, não
qualidade de geração de texto.

### 9.3 Template de resultado — **VAZIO**

> Nenhuma execução foi realizada. Preencher exclusivamente a partir de
> `artifacts/metrics/verificacao_llm.json`.

**Taxa global**

| Métrica | Valor |
|---|---|
| Sínteses tentadas | — |
| Descartadas | — |
| Taxa de rejeição | — |
| Aprovadas com aviso (regras 4/5) | — |

**Por motivo de descarte**

| Motivo | Ocorrências | % dos descartes |
|---|---|---|
| `numero_orfao` | — | — |
| `contradicao_rotulo` | — | — |
| `rotulo_ausente` | — | — |
| `secao_faltante` | — | — |
| `aviso_ausente` | — | — |
| `repeticao` | — | — |
| `violacao_clinica` | — | — |
| `texto_curto` | — | — |
| falha de execução | — | — |

**Por variante de prompt**

| Variante | Tentativas | Descartes | Taxa |
|---|---|---|---|
| A — base | — | — | — |
| B — técnica | — | — | — |
| C — clínica | — | — | — |
| D — dados incompletos | — | — | — |
| E — bypass emergência | — | — | — |
| F — modo degradado | — | — | — |

**Diagnóstico do trade-off de §4.4**

| Métrica | Valor |
|---|---|
| Numerais justificados só por coincidência com protocolo | — |
| Execuções em que isso ocorreu | — |

### 9.4 O que será feito com uma taxa alta

Comprometimento antecipado, para que a decisão não seja tomada sob pressão do resultado:

| Se a taxa for | Ação permitida | Ação proibida |
|---|---|---|
| Alta por `numero_orfao` | Reforçar camada 1: reduzir números injetados, usar variante C | Afrouxar `TOLERANCIA` |
| Alta por `aviso_ausente` | Mover os avisos para concatenação pós-geração determinística, tirando-os do que o LLM precisa copiar | Tornar os avisos opcionais |
| Alta por `repeticao` | Ajustar `repetition_penalty` / `no_repeat_ngram_size` | Aumentar `MAX_REPETICOES_NGRAMA` |
| Alta por `violacao_clinica` | Reforçar o system prompt | Rebaixar violação para aviso |
| Alta em geral | Reportar a taxa e recomendar o modo estruturado como padrão | Omitir a taxa do relatório |

A última linha é a mais importante. **Se o LLM de 3B se mostrar incapaz de passar na verificação de
forma consistente, a conclusão honesta é que o valor agregado dele nesta tarefa é baixo** — e isso
é um resultado legítimo a reportar, não um fracasso a esconder. A resposta estruturada existe
justamente para que essa conclusão seja tecnicamente suportável.

---

## 10. O que esta política não cobre

Limites declarados, para que não sejam confundidos com garantias:

| Não coberto | Por quê |
|---|---|
| Alucinação **sem número** ("associada a maior chance de complicação") | Afirmação clínica vaga não é detectável por regex. Mitigação parcial: as regras 1 e 2 do validador |
| Conduta plausível mas ausente do protocolo recuperado | O verificador não faz *entailment* entre texto e `trecho`. Mitigação: a política de citação exige fonte por conduta (`docs/rag/POLITICA_DE_CITACAO.md`) |
| Número correto usado em contexto errado ("limiar de 0,31 de probabilidade de óbito") | O verificador confere o valor, não o referente |
| Omissão de fator relevante de `top_features` | O verificador não exige completude, só ausência de invenção |
| Erro na própria camada de ML | Fora do escopo. Ver `docs/ml/LIMITACOES_DO_MODELO.md` |

A política **impede números inventados e contradição de rótulo**. Ela não torna o texto
clinicamente correto. Essa distinção precisa aparecer no relatório e na apresentação.

---

## 11. Estado atual

| Item | Estado |
|---|---|
| `lib/validacao.py` | **Não existe** |
| `ValidadorDeterministico` promovido | **Não** — segue em `referencias/` |
| Os 6 casos do `__main__` como teste automatizado | **Não** |
| Verificação numérica implementada | **Não** |
| Coerência de rótulo implementada | **Não** |
| `resposta_estruturada` implementada | **Não** |
| Taxa de rejeição medida | **Não** — tabelas da §9.3 vazias por decisão |
