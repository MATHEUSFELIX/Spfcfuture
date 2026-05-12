# Test Explainability — SPFC Champion Decision OS

Este documento atende ao princípio constitucional de **Explicabilidade obrigatória** (Princípio 6) e ao requisito da página **Test Health**. Ele detalha as categorias de testes do sistema, explicando o que validam, por que importam e fornecendo exemplos de implementação.

A qualidade de um sistema de decisão esportiva não é medida apenas pela sofisticação de seus modelos táticos, mas pela robustez de suas garantias de corretude. O sistema não pode inventar dados, e falhas não podem ser suprimidas silenciosamente. As suítes de testes são as barreiras arquiteturais que impõem essas restrições.

---

## 1. Domain Models

Os testes de Domain Models asseguram a integridade das estruturas de dados centrais do sistema, como `Player`, `Team`, `Match`, `PlayState`, `TacticalBranch`, `SquadProfile`, `OpponentProfile`, `ScoutingTarget` e `DecisionReport`.

Esta categoria valida que os modelos de domínio possuem validação correta, serialização consistente, defaults seguros e erros claros quando instanciados com dados inválidos. A integridade dos modelos é fundamental porque eles são a base de toda a lógica de decisão. Um modelo com validação fraca pode aceitar dados corrompidos silenciosamente, violando o princípio de rastreabilidade total e contaminando as análises subsequentes.

**Exemplos de testes:**
*   `test_run_summary_serialization`: Garante que `RunSummary` serializa e desserializa corretamente via métodos `to_dict` e `from_dict`.
*   `test_run_summary_defaults`: Garante que `RunSummary` tem defaults seguros e não aceita status inválido.
*   `test_run_detail_structure`: Garante que `RunDetail` contém todos os campos obrigatórios.

## 2. Pipeline

Os testes de Pipeline cobrem o fluxo completo de ingestão, normalização e geração de artefatos. Eles avaliam o carregamento de dados, a rejeição de payloads inválidos, a geração de diagnósticos e a persistência de resultados.

O pipeline é o coração operacional do sistema. Se ele aceitar dados inválidos silenciosamente ou falhar sem um diagnóstico claro, todas as análises subsequentes serão comprometidas. A regra de ouro imposta por esses testes é: payload ruim não entra no sistema.

**Exemplos de testes:**
*   `test_artifact_store_list_runs_empty`: Garante que o `ArtifactStore` retorna execuções de demonstração quando não há artefatos reais disponíveis.
*   `test_artifact_store_invalid_json`: Garante que um arquivo JSON inválido é reportado como erro e não aceito silenciosamente.

## 3. Context and Priors

Esta categoria valida que o contexto de jogo (estado do placar, fase da partida, histórico de decisões) é carregado corretamente e que os *priors* táticos são aplicados de forma rastreável nas simulações.

Decisões táticas dependem fortemente de contexto. Um sistema que ignora o estado do jogo (por exemplo, a necessidade de defender uma vantagem de 1 a 0 nos minutos finais) pode gerar recomendações inadequadas. O contexto deve ser explícito, rastreável e auditável, o que é garantido por esta suíte.

**Exemplos de testes:**
*   `test_play_state_context`: Garante que `PlayState` carrega a fase da partida, o placar e a posse de bola corretamente.

## 4. Viewer

Os testes de Viewer garantem que o visualizador 2D renderiza corretamente as posições dos jogadores, as trajetórias da bola e os *branches* táticos, sem distorções espaciais ou erros de coordenadas.

A visualização é a principal interface de revisão humana. Erros de renderização podem levar a interpretações incorretas de lances e comprometer a qualidade das decisões finais tomadas pela comissão técnica.

**Exemplos de testes:**
*   `test_viewer_renders_positions`: Garante que as posições dos jogadores são renderizadas estritamente dentro dos limites do campo.

## 5. Video-to-State

Esta categoria avalia a conversão de feeds de vídeo ou dados brutos de tracking para instâncias de `PlayState`. Ela verifica a extração de coordenadas, a identificação de jogadores, a detecção da fase de jogo e a métrica de confiança da extração.

A qualidade da extração de estado a partir de vídeo determina a confiabilidade de toda a análise subsequente. Extrações com baixa confiança devem ser sinalizadas explicitamente para revisão humana, impedindo que dados ruidosos corrompam as métricas táticas.

**Exemplos de testes:**
*   `test_video_extraction_confidence`: Garante que extrações com confiança abaixo do limiar configurado são marcadas obrigatoriamente para revisão.

## 6. Runtime Ingestion

Os testes de Runtime Ingestion validam a ingestão em tempo real de dados de tracking, eventos de jogo e feeds externos. Eles medem a latência, validam schemas, asseguram a rejeição de dados corrompidos e verificam a geração de alertas.

Durante a partida, dados chegam em alta frequência. O sistema deve processar, validar e rejeitar dados inválidos sem travar o pipeline principal ou aceitar silenciosamente informações corrompidas que poderiam prejudicar a análise no intervalo ou no pós-jogo.

**Exemplos de testes:**
*   `test_ingestion_rejects_bad_schema`: Garante que um payload com schema inválido é rejeitado com um erro descritivo, não travando o processo de ingestão.

## 7. Workflow and Review

Esta categoria valida os workflows de orquestração do sistema, incluindo a sequência de execução dos agentes, a geração do `DecisionReport`, o registro do feedback humano e a rastreabilidade de cada recomendação até sua evidência de origem.

O workflow é a etapa onde a análise de dados se transforma em uma recomendação acionável. Cada recomendação deve ter uma evidência rastreável, e o feedback humano deve ser devidamente registrado para permitir a calibração contínua dos modelos.

**Exemplos de testes:**
*   `test_workflow_generates_report`: Garante que a execução completa do workflow gera um `DecisionReport` contendo todos os campos obrigatórios.
*   `test_human_feedback_recorded`: Garante que o feedback humano é persistido corretamente e associado ao ID da execução correspondente.

## 8. Governance and Observability

Os testes de Governance and Observability asseguram o funcionamento dos mecanismos de governança do sistema: logs de auditoria, rastreabilidade de decisões, alertas de qualidade de dados e geração de relatórios de confiança.

A rastreabilidade total é um princípio fundamental do SPFC Champion Decision OS. Toda decisão gerada pelo sistema deve ser completamente auditável: quem recomendou, com base em qual evidência, com qual nível de confiança e qual foi o resultado real observado.

**Exemplos de testes:**
*   `test_audit_log_created`: Garante que cada execução (run) do pipeline gera uma entrada imutável no log de auditoria.

## 9. API and CLI

Esta suíte valida os contratos da API interna e da interface de linha de comando (CLI). Ela verifica as rotas web, os schemas de requisição e resposta, o tratamento de erros e a execução do comando `football-os app` e seus subcomandos.

A API e o CLI são as interfaces primárias de integração do sistema. Contratos quebrados silenciosamente podem causar falhas em cascata em pipelines automatizados e ferramentas de análise externas. Além disso, falhas na API não devem expor *stack traces* brutos aos usuários.

**Exemplos de testes:**
*   `test_health_endpoint_returns_200`: Garante que a requisição `GET /health` retorna status 200 com os metadados de versão.
*   `test_home_page_renders`: Garante que a página inicial renderiza o HTML corretamente sem erros.
*   `test_run_detail_404_for_unknown`: Garante que a requisição de um `run_id` inexistente retorna status 404 com uma mensagem amigável ao usuário.
*   `test_cli_app_command_exists`: Garante que o comando `football-os app` está registrado corretamente no grupo do CLI.

## 10. Pilot Evaluation

Os testes de Pilot Evaluation cobrem o ciclo completo de testes em cenários piloto. Eles validam a seleção de cenários reais, a execução de workflows, a coleta de feedback humano e a geração de um relatório de piloto com métricas de qualidade consolidadas.

A fase de piloto é a validação final do sistema em condições próximas ao uso real no clube. Sem uma avaliação sistemática do piloto, não é possível calibrar a confiança do sistema ou identificar lacunas críticas antes da adoção completa.

**Exemplos de testes:**
*   `test_pilot_report_generated`: Garante que o relatório de piloto é gerado contendo métricas de qualidade e o feedback consolidado.
