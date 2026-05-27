# Templates de Documentos Clínicos

Modelos especializados de documentos referenciados no enunciado da Fase 3, requisito:
> "Modelos especializados de documentos: Laudos de mamografias e ultrassons ginecológicos; Receitas para terapias hormonais e medicações específicas; Procedimentos de colposcopia e biópsias; Relatórios de atendimento a vítimas de violência; Protocolos de pré-natal e puerpério."

Cada template segue o padrão Markdown com **placeholders no formato `{{campo}}`** que podem ser preenchidos programaticamente (`.format()`, Jinja2, ou substituição direta).

## Disponíveis

| Arquivo | Uso clínico | Base normativa |
|---|---|---|
| [`laudo_mamografia_birads.md`](laudo_mamografia_birads.md) | Laudo de mamografia digital, classificação BI-RADS® | Colégio Brasileiro de Radiologia, ACR |
| [`laudo_colposcopia_biopsia.md`](laudo_colposcopia_biopsia.md) | Laudo de colposcopia + biópsia/AP de colo uterino (IFCPC 2011) | INCA, IFCPC, FEBRASGO |
| [`receita_terapia_hormonal.md`](receita_terapia_hormonal.md) | Receita de contraceptivo hormonal (COC, POP, DIU hormonal) ou TRH | FEBRASGO, ANVISA, MS |
| [`acompanhamento_prenatal_puerperio.md`](acompanhamento_prenatal_puerperio.md) | Caderneta de pré-natal + 2 consultas puerperais (com EPDS) | MS — Caderneta da Gestante 2022, FEBRASGO, OMS |
| [`ficha_notificacao_sinan_violencia.md`](ficha_notificacao_sinan_violencia.md) | Ficha de Notificação Compulsória de Violência Interpessoal/Autoprovocada | SINAN — Ministério da Saúde |
| [`relatorio_atendimento_violencia.md`](relatorio_atendimento_violencia.md) | Relatório circunstanciado de atendimento à mulher vítima de violência | Norma Técnica MS, Lei Maria da Penha |

## Como usar

### Programaticamente (Python)

```python
from pathlib import Path

tpl = Path('lib/templates/laudo_mamografia_birads.md').read_text(encoding='utf-8')
laudo = tpl.format(
    paciente_nome='Maria Silva',
    paciente_idade=58,
    data_exame='2026-05-25',
    birads_categoria=2,
    observacoes='Achados benignos. Manter rotina bienal.',
    # ... outros campos
)
```

### Via Jinja2 (recomendado para templates complexos)

```python
from jinja2 import Template
tpl = Template(Path('lib/templates/receita_terapia_hormonal.md').read_text())
receita = tpl.render(paciente={...}, medicamento={...}, posologia={...})
```

## Limitações reconhecidas

- **Não substituem laudo emitido por radiologista habilitado ou prescrição médica.** São esqueletos para autopreenchimento + revisão profissional obrigatória.
- **Não incluem assinatura digital ICP-Brasil** — em produção, integrar com prestador de certificação digital.
- **Não cobrem todas as variações** de cada documento clínico; são exemplos representativos para demonstrar a capacidade do sistema de gerar saídas estruturadas no padrão hospitalar.

## Integração futura com workflows

Os workflows LangGraph atuais (`lib/workflows/`) já geram saídas estruturadas. Em iteração futura, os campos do estado final podem alimentar diretamente esses templates:

- `lib/workflows/violencia.py` → `relatorio_atendimento_violencia.md` + `ficha_notificacao_sinan_violencia.md`
- `lib/workflows/prevencao.py` → solicitação de mamografia (que após realizada vira `laudo_mamografia_birads.md`); citologia alterada → colposcopia/biópsia → `laudo_colposcopia_biopsia.md`
- `lib/workflows/obstetrico.py` → registro estruturado a cada consulta → `acompanhamento_prenatal_puerperio.md` (seções 5-11)
- Tool `consultar_medicamento` + paciente em contexto → `receita_terapia_hormonal.md`

Isso permitiria o assistente entregar não só orientações em chat, mas **documentos clínicos prontos para revisão e assinatura do profissional** — fechando o ciclo "consulta → conduta → documento formal".
