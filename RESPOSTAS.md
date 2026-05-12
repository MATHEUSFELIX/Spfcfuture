# Respostas para Início da Implementação

1. **Comando de teste completo:**
   `pytest` (conforme definido no 07_EVALUATION_GATES.md)

2. **Plano de implementação:**
   - **Passo 1:** Configurar ambiente básico e dependências (FastAPI, uvicorn, jinja2, pytest).
   - **Passo 2:** Criar estrutura do pacote (`src/web`, `src/cli`, `tests/`).
   - **Passo 3:** Implementar o Web App Local (FastAPI + Jinja2) com as rotas: Home, Runs, Detalhe de Run, Healthcheck e Test Health.
   - **Passo 4:** Criar o CLI com o comando `football-os app` para iniciar o servidor web.
   - **Passo 5:** Escrever `TEST_EXPLAINABILITY.md` detalhando as categorias de teste.
   - **Passo 6:** Criar os testes unitários e de integração para a web app e CLI.
   - **Passo 7:** Rodar `pytest` para garantir que tudo passe.
   - **Passo 8:** Atualizar o `README.md` e realizar commit/push.

3. **Primeiro arquivo a modificar:**
   `pyproject.toml` ou `requirements.txt` (para definir as dependências), seguido de `src/web/local_app.py` (para criar a base do Web App). Como o repositório está vazio, o primeiro passo é criar a estrutura inicial.

4. **Testes que vai criar:**
   - Testes das rotas do FastAPI (Home, Runs, Healthcheck, Test Health) usando `TestClient`.
   - Testes do CLI para garantir que o comando `football-os app` seja reconhecido.
   - Testes do catálogo de testes para garantir que as explicações de health sejam geradas corretamente.

5. **Riscos que vai monitorar:**
   - **Falta de dados reais:** Como não posso inventar dados, precisarei usar fixtures determinísticas e claras para simular "runs" e cenários.
   - **Acoplamento excessivo:** A UI não pode conter lógica tática. A separação entre o Web App e o Core (mesmo que mockado por enquanto) deve ser estrita.
   - **Falhas silenciosas:** Garantir que erros sejam reportados claramente na UI (sem stack traces crus) conforme 06_APP_UX.md.
   - **Regressão:** O repositório está vazio, mas ao longo da implementação, garantir que o comando `pytest` rode no Gate 0 e em cada passo sem falhar.
