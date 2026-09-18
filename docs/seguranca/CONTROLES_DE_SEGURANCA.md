# Controles de segurança

**Agente responsável:** `SecurityAndComplianceAgent`
**Status:** Política normativa. Controles de *código novo* ainda não implementados. Controles da Fase 3 estão marcados `[COD]`.

## 1. Postura

O sistema trata dados de saúde da mulher, violência e prontuário. Mesmo sintéticos, o código deve assumir **dado pessoal sensível** (LGPD art. 11). Controles abaixo aplicam-se à evolução e ao que já existe.

## 2. Controles existentes `[COD]`

| ID | Controle | Onde | Limite |
|---|---|---|---|
| C-01 | `log_acesso` em consulta/registro de violência | `lib/tools.py`, `lib/db.py` | Não cobre decisões clínicas |
| C-02 | Motivo ≥ 5 caracteres em `consultar_violencia` | `tools.py` | Contagem na UI bypassa o caminho (`ui.py:63-66`) |
| C-03 | Confirmação clínica para gravar SINAN | `ui.py` + `violencia.py` | Único HIL formal |
| C-04 | Disclaimer de uso na UI | `ui.py` | Texto de apresentação, não campo do contrato |
| C-05 | Adapter e DB gitignored | `.gitignore` | Artefatos vivem no Drive |

## 3. Controles a implementar (nova fase)

| ID | Controle | Tarefa | Critério |
|---|---|---|---|
| C-10 | Config por env; zero segredo no git | T-08, T-09, T-57 | `test_sem_segredos.py` |
| C-11 | Flag `ML_RISCO_HABILITADO` default 0 | T-08, T-45 | obstétrico idêntico |
| C-12 | Tabela `predicoes_ml` sem valores clínicos | T-35, T-36 | só `features_hash` |
| C-13 | Auditoria de **toda** invocação, inclusive erro | T-36, T-49 | 1 linha / request |
| C-14 | Regras de alarme **antes** do ML | T-41 | teste de bypass |
| C-15 | HIL em dados incompletos | T-41 | sem imputação de obrigatório |
| C-16 | LLM não altera números | T-38 | descarte |
| C-17 | Avisos clínicos estruturados | T-39, T-51 | dois avisos sempre |
| C-18 | Perfil Docker sem pesos nem `HF_TOKEN` | T-58 | imagem `demo-cpu` |
| C-19 | `pip-audit` + varredura | T-63 | zero crítica aberta ou aceite documentado |
| C-20 | Truncamento de citação fiel ao prompt | T-43 | sem `doc_id` fantasma |

## 4. Segregação

| Superfície | Pode ver | Não pode ver |
|---|---|---|
| UI do profissional logado | Predição, P, explicação, trechos de protocolo | Pesos do modelo, `risco_latente`, features de outras pacientes |
| Tabela `predicoes_ml` | Hash, modo, versões, contribuições sem `value` | PA, Hb, infecção, texto livre de violência |
| Logs estruturados | `correlation_id`, nó, duração, modo | Payload clínico cru |
| Dataset sintético | Features de gestações fictícias | Qualquer linha de `hospital.db` real (hoje já é Faker) |

## 5. Autenticação e sessão

Fora de escopo desta fase: não há IdP. O campo `Profissional logado` é um textbox. Dívida conhecida (LAC-10, `_USUARIO_ATUAL` global). Controle mitigador: não tratar esse identificador como autenticação; documentar no aviso de demo.

## 6. Referências

`ANALISE_DE_RISCOS.md` · `LGPD_E_PRIVACIDADE.md` · `POLITICA_DE_AUDITORIA.md` · `AVISOS_DE_USO_CLINICO.md`
