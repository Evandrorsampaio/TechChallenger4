# Plano de testes

Pirâmide: unit (`tests/unit`) → integration (`tests/integration`) → e2e (`tests/e2e`) → regression (`tests/regression`).

Fixtures em `tests/conftest.py`: SQLite temporário, `FakeChatModel`, `FakeRetriever`, `CASO_OK`.

Não usar GPU nem rede no perfil ml-only.
