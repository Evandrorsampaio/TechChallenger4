# Avisos de uso clínico

**Agente responsável:** `SecurityAndComplianceAgent`
**Status:** Texto normativo. Deve aparecer na UI, no payload, no README e no roteiro de demo. Ainda não está como campo estruturado nos workflows atuais (`[COD]` só disclaimer livre em `lib/ui.py`).

Estes avisos **não são opcionais**. T-39 torna `safety_notice` e `aviso_dados_sinteticos` constantes de módulo. Teste: `tests/unit/test_avisos_obrigatorios.py`.

---

## Aviso 1 — Apoio à decisão (`safety_notice`)

> Resultado de apoio à decisão. Não realiza diagnóstico definitivo. Não substitui profissionais de saúde. Não deve ser utilizado como única fonte de decisão. Situações críticas devem ser encaminhadas para avaliação humana.

Uso: todo modo (`normal`, `degradado`, `bypass_regra`, `incompleto`).

## Aviso 2 — Dados sintéticos (`aviso_dados_sinteticos`)

> Modelo treinado em dados sintéticos, gerados programaticamente para demonstração. As métricas medem a recuperação de um processo gerador definido por esta equipe. Não há validação clínica em população real. Não interpretar desempenho como evidência assistencial.

Uso: todo modo, inclusive quando o ML nem rodou (para não sugerir que o restante do sistema foi “clinicamente validado”).

## Aviso 3 — Incerteza

A interface deve mostrar, no mesmo bloco da classificação:

- probabilidade da classe positiva;
- limiar operacional aplicado;
- campos imputados (nomeados);
- método de explicabilidade (`explanation_method`).

Omitir o limiar é uma forma de superconfiança.

## Aviso 4 — Emergência / bypass

Quando `modo='bypass_regra'`:

> Encaminhamento imediato por regra determinística de alarme obstétrico. A probabilidade do modelo não foi utilizada nesta decisão.

## Aviso 5 — Modo degradado

Quando `modo='degradado'`:

> Modelo de ML indisponível. Classificação pela regra determinística de critérios de alto risco. Qualidade distinta da inferência supervisionada.

Deve aparecer na **primeira** seção da resposta, não no rodapé.

## Aviso 6 — Dados incompletos

> Não houve predição. Campos obrigatórios ausentes: [lista]. Completar os dados e resubmeter. Não foram imputados valores obrigatórios.

## Aviso 7 — Docker / dublê de LLM

No `GUIA_DEMO.md` e no README do perfil `demo-cpu`:

> Esta execução usa um dublê determinístico de chat (`FakeChatModel`) no lugar do Llama 3.2 3B. Serve para validar o pipeline e o contêiner. Não é evidência de qualidade do LLM fine-tuned.

## Linguagem proibida

- “diagnóstico”
- “confirma a doença”
- “validado clinicamente” / “aprovado para uso assistencial”
- “esta variável causou o risco”
- “Docker funcional” sem apontar o log de build/run
- “procure um profissional de saúde” como se o usuário não fosse o profissional (já proibido no `SYSTEM_PROMPT` do ReAct)

## Onde replica

| Superfície | Avisos |
|---|---|
| Payload LLM | 1 e 2 sempre; 4–6 conforme modo |
| Aba Gradio nova | 1–6 visíveis |
| `predicoes_ml` | modo implica qual aviso valeu; textos não precisam ser duplicados se o modo for fiel |
| README / demo / vídeo | 1, 2 e 7 |

## Relação com a Fase 3

O disclaimer atual da UI permanece nas 5 abas antigas. Não removê-lo. A 6ª aba adiciona os campos estruturados. Unificar o texto das 5 abas com o Aviso 1 é Should (T-71/higiene), não Must.
