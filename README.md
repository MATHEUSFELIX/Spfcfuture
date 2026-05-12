# SPFC Champion Decision OS

Sistema de Apoio a Decisões Esportivas do São Paulo FC.

Este sistema não promete títulos. Ele melhora a qualidade das decisões em análise de jogo, simulação tática, elenco, scouting, preparação de adversário, bola parada, revisão pós-jogo e governança com feedback humano.

> **Princípio fundamental:** Assistente, não oráculo. Evidência acima de narrativa. Decisão final é sempre humana.

---

## Quickstart

### Pré-requisitos

- Python 3.11+
- pip

### Instalação

```bash
git clone https://github.com/MATHEUSFELIX/Spfcfuture.git
cd Spfcfuture
pip install -r requirements.txt
pip install -e .
```

### Iniciar o Web App

```bash
football-os app
```

O sistema abrirá automaticamente em `http://127.0.0.1:8000`.

### Opções do comando `app`

| Opção | Padrão | Descrição |
|---|---|---|
| `--host` | `127.0.0.1` | Host do servidor web |
| `--port` | `8000` | Porta do servidor web |
| `--reload` | desabilitado | Hot-reload para desenvolvimento |
| `--no-browser` | desabilitado | Não abre o navegador automaticamente |

### Verificar saúde do sistema

```bash
football-os health
```

### Rodar os testes

```bash
pytest
```

---

## Páginas do Web App

| Rota | Descrição |
|---|---|
| `/` | Home — visão geral do sistema e runs recentes |
| `/runs` | Lista de todas as execuções (runs) do pipeline |
| `/runs/{run_id}` | Detalhe completo de uma run |
| `/health` | Healthcheck JSON da aplicação |
| `/test-health` | Catálogo de testes com explicações completas |
| `/api/docs` | Documentação interativa da API (Swagger UI) |
| `/api/runs` | Lista de runs em JSON |
| `/api/runs/{run_id}` | Detalhe de run em JSON |
| `/api/test-catalog` | Catálogo de testes em JSON |
| `/knowledge-base` | Base de Conhecimento do clube e modelo de jogo |
| `/squad` | Análise de Elenco, profundidade e lacunas |
| `/api/knowledge-base` | Base de Conhecimento em JSON |
| `/api/squad` | Análise de Elenco em JSON |
| `/api/squad/gaps` | Lacunas do elenco em JSON |

---

## Estrutura do Projeto

```
Spfcfuture/
├── src/
│   ├── core/
│   │   ├── models.py          # Modelos de domínio da Fase 1
│   │   ├── football_models.py # Modelos de domínio do futebol (Team, Player, Match)
│   │   ├── artifact_store.py  # Carregador de artefatos de runs
│   │   └── test_catalog.py    # Catálogo de categorias de testes
│   ├── spfc_base/
│   │   ├── knowledge_base.py  # Identidade, modelo de jogo e princípios
│   │   └── decision_memory.py # Repositório de memória de decisões
│   ├── squad_intelligence/
│   │   ├── squad_analyzer.py  # Analisador de elenco, profundidade e gaps
│   │   └── squad_fixtures.py  # Dados de demonstração de elenco
│   ├── web/
│   │   ├── local_app.py       # Web App FastAPI
│   │   ├── templates/         # Templates Jinja2
│   │   │   ├── base.html
│   │   │   ├── home.html
│   │   │   ├── runs.html
│   │   │   ├── run_detail.html
│   │   │   ├── test_health.html
│   │   │   ├── knowledge_base.html
│   │   │   ├── squad.html
│   │   │   └── error.html
│   │   └── static/css/
│   │       └── style.css      # Estilos SPFC (vermelho, preto, branco)
│   └── cli/
│       └── main.py            # CLI com comando football-os app
├── tests/
│   ├── core/
│   │   ├── test_models.py         # Testes de domain models
│   │   ├── test_artifact_store.py # Testes do pipeline/artifact store
│   │   └── test_test_catalog.py   # Testes do catálogo de testes
│   ├── spfc_base/
│   │   ├── test_knowledge_base.py # Testes da base de conhecimento
│   │   └── test_decision_memory.py# Testes da memória de decisões
│   ├── squad_intelligence/
│   │   ├── test_squad_analyzer.py # Testes do analisador de elenco
│   │   └── test_squad_fixtures.py # Testes das fixtures de elenco
│   ├── web/
│   │   ├── test_routes.py         # Testes de integração das rotas da Fase 1
│   │   └── test_phase2_routes.py  # Testes de integração das rotas da Fase 2
│   └── cli/
│       └── test_cli.py            # Testes do CLI
├── TEST_EXPLAINABILITY.md     # Explicação completa das categorias de testes
├── ROADMAP.md                 # Roadmap de desenvolvimento
├── pyproject.toml             # Configuração do pacote
└── requirements.txt           # Dependências
```

---

## Módulos do Sistema

| Módulo | Descrição | Status |
|---|---|---|
| Local Web App | Interface web local para análise, revisão e feedback | **Ativo** |
| Match Intelligence | Análise de jogos, adversários, padrões e riscos | Planejado |
| Tactical Simulator | Simulação de lances, branches, xT e controle de espaço | Planejado |
| Squad Intelligence | Elenco, profundidade, lacunas e desenvolvimento | **Ativo** |
| Scouting & Market Fit | Jogadores-alvo por encaixe tático, custo e risco | Planejado |
| Set Piece Lab | Bola parada ofensiva e defensiva | Planejado |
| Matchday Assistant | Pré-jogo, intervalo e pós-jogo | Planejado |
| Board Dashboard | Visão executiva de investimento, risco e impacto | Planejado |

---

## Testes

O projeto segue os **Evaluation Gates** definidos nas especificações:

- **Gate 0 — Baseline:** `pytest` deve passar antes de qualquer desenvolvimento.
- **Gate 1 — Unit:** Cada módulo novo tem testes unitários.
- **Gate 2 — Integration:** Fluxos entre módulos têm testes de integração.
- **Gate 3 — Regression:** Suite completa roda antes de concluir cada fase.
- **Gate 4 — Documentation:** README, quickstart e TEST_EXPLAINABILITY atualizados.

Para entender o que cada categoria de testes valida e por que importa, consulte o arquivo [`TEST_EXPLAINABILITY.md`](TEST_EXPLAINABILITY.md) ou acesse a página `/test-health` no web app.

### Resultado atual

```
331 passed, 0 failed
```

---

## Princípios Constitucionais

O sistema é regido por 10 princípios inegociáveis:

1. Assistente, não oráculo.
2. Evidência acima de narrativa.
3. Não inventar dados.
4. Separar fato, inferência e recomendação.
5. Testes antes de avançar.
6. Explicabilidade obrigatória.
7. Simulações são cenários, não certezas.
8. Decisão final é humana.
9. Rastreabilidade total.
10. Produto usável por analistas, comissão e diretoria.

### Proibições

- Não prometer título.
- Não inventar estatísticas, lesões, salários ou bastidores.
- Não recomendar decisão médica.
- Não deixar payload ruim entrar silenciosamente.
- Não avançar com testes falhando.

---

## Roadmap

| Fase | Entrega | Status |
|---|---|---|
| 1 | Local Web App + Test Explainability | **Concluído** |
| 2 | Base São Paulo: knowledge base e modelo de jogo | **Concluído** |
| 3 | Squad Intelligence: elenco, papéis e lacunas | **Concluído** |
| 4 | Opponent Preparation: adversário e plano pré-jogo | Planejado |
| 5 | Scouting & Market Fit: contratações por encaixe | Planejado |
| 6 | Set Piece Lab: bola parada | Planejado |
| 7 | Matchday Assistant: pré-jogo, intervalo, pós-jogo | Planejado |
| 8 | Pilot com revisão humana | Planejado |
| 9 | Produto interno | Planejado |
| 10 | Inteligência avançada e calibration | Planejado |

---

## Licença

Uso interno — São Paulo FC. Todos os direitos reservados.
