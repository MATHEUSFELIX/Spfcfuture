"""
Test Catalog — Catálogo explicativo das categorias de testes do sistema.

Princípio: Explicabilidade obrigatória (00_CONSTITUTION.md, princípio 6).
Cada categoria documenta: o que valida, por que importa, exemplos e status.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class TestExample:
    """Exemplo de teste em uma categoria."""
    name: str
    description: str
    file_hint: str = ""


@dataclass
class TestCategory:
    """
    Categoria de testes do sistema com explicação completa.

    Atributos:
        id: Identificador único da categoria.
        title: Nome legível da categoria.
        what_it_validates: O que os testes desta categoria validam.
        why_it_matters: Por que esta categoria é importante para o sistema.
        examples: Lista de exemplos de testes nesta categoria.
        status: Status atual ('active', 'planned', 'partial').
    """
    id: str
    title: str
    what_it_validates: str
    why_it_matters: str
    examples: List[TestExample] = field(default_factory=list)
    status: str = "planned"

    @property
    def status_label(self) -> str:
        labels = {
            "active": "Ativo",
            "planned": "Planejado",
            "partial": "Parcial",
        }
        return labels.get(self.status, self.status)

    @property
    def status_css_class(self) -> str:
        classes = {
            "active": "status-active",
            "planned": "status-planned",
            "partial": "status-partial",
        }
        return classes.get(self.status, "status-planned")


# Catálogo completo de categorias de testes
TEST_CATALOG: List[TestCategory] = [
    TestCategory(
        id="domain_models",
        title="Domain Models",
        what_it_validates=(
            "Valida que os modelos de domínio (Player, Team, Match, PlayState, "
            "TacticalBranch, SquadProfile, OpponentProfile, ScoutingTarget, "
            "DecisionReport) possuem validação correta, serialização, defaults "
            "seguros e erros claros."
        ),
        why_it_matters=(
            "Os modelos são a base de toda a lógica de decisão. Um modelo com "
            "validação fraca pode aceitar dados inválidos silenciosamente, "
            "violando o princípio de rastreabilidade total e contaminando "
            "análises subsequentes."
        ),
        examples=[
            TestExample(
                name="test_run_summary_serialization",
                description="Garante que RunSummary serializa e desserializa corretamente via to_dict/from_dict.",
                file_hint="tests/core/test_models.py",
            ),
            TestExample(
                name="test_run_summary_defaults",
                description="Garante que RunSummary tem defaults seguros e não aceita status inválido.",
                file_hint="tests/core/test_models.py",
            ),
            TestExample(
                name="test_run_detail_structure",
                description="Garante que RunDetail contém todos os campos obrigatórios.",
                file_hint="tests/core/test_models.py",
            ),
        ],
        status="active",
    ),
    TestCategory(
        id="pipeline",
        title="Pipeline",
        what_it_validates=(
            "Valida o fluxo completo de ingestão, normalização e geração de "
            "artefatos: carregamento de dados, rejeição de payload inválido, "
            "geração de diagnósticos e persistência de resultados."
        ),
        why_it_matters=(
            "O pipeline é o coração do sistema. Se ele aceitar dados inválidos "
            "silenciosamente ou falhar sem diagnóstico claro, todas as análises "
            "subsequentes serão comprometidas. A regra é: payload ruim não entra."
        ),
        examples=[
            TestExample(
                name="test_artifact_store_list_runs_empty",
                description="Garante que o ArtifactStore retorna demos quando não há artefatos reais.",
                file_hint="tests/core/test_artifact_store.py",
            ),
            TestExample(
                name="test_artifact_store_invalid_json",
                description="Garante que JSON inválido é reportado como erro, não aceito silenciosamente.",
                file_hint="tests/core/test_artifact_store.py",
            ),
        ],
        status="active",
    ),
    TestCategory(
        id="context_and_priors",
        title="Context and Priors",
        what_it_validates=(
            "Valida que o contexto de jogo (estado do placar, fase da partida, "
            "histórico de decisões) é carregado corretamente e que os priors "
            "táticos são aplicados de forma rastreável."
        ),
        why_it_matters=(
            "Decisões táticas dependem fortemente de contexto. Um sistema que "
            "ignora o estado do jogo (ex: vencer por 1 a 0 no último minuto) "
            "pode gerar recomendações inadequadas. O contexto deve ser explícito "
            "e auditável."
        ),
        examples=[
            TestExample(
                name="test_play_state_context",
                description="Garante que PlayState carrega fase, placar e posse corretamente.",
                file_hint="tests/core/test_context.py",
            ),
        ],
        status="planned",
    ),
    TestCategory(
        id="viewer",
        title="Viewer",
        what_it_validates=(
            "Valida que o viewer 2D renderiza corretamente posições de jogadores, "
            "trajetórias de bola e branches táticos sem distorções ou erros de "
            "coordenadas."
        ),
        why_it_matters=(
            "A visualização é a principal interface de revisão humana. Erros de "
            "renderização podem levar a interpretações incorretas de lances e "
            "comprometer a qualidade das decisões da comissão técnica."
        ),
        examples=[
            TestExample(
                name="test_viewer_renders_positions",
                description="Garante que posições de jogadores são renderizadas dentro dos limites do campo.",
                file_hint="tests/viewer/test_viewer.py",
            ),
        ],
        status="planned",
    ),
    TestCategory(
        id="video_to_state",
        title="Video-to-State",
        what_it_validates=(
            "Valida a conversão de vídeo ou tracking para PlayState: extração de "
            "coordenadas, identificação de jogadores, detecção de fase de jogo e "
            "confiança da extração."
        ),
        why_it_matters=(
            "A qualidade da extração de estado a partir de vídeo determina a "
            "confiabilidade de toda a análise. Extrações com baixa confiança devem "
            "ser sinalizadas explicitamente para revisão humana."
        ),
        examples=[
            TestExample(
                name="test_video_extraction_confidence",
                description="Garante que extrações com confiança abaixo do limiar são marcadas para revisão.",
                file_hint="tests/ingestion/test_video_to_state.py",
            ),
        ],
        status="planned",
    ),
    TestCategory(
        id="runtime_ingestion",
        title="Runtime Ingestion",
        what_it_validates=(
            "Valida a ingestão em tempo real de dados de tracking, eventos e "
            "feeds externos: latência, validação de schema, rejeição de dados "
            "corrompidos e geração de alertas."
        ),
        why_it_matters=(
            "Durante a partida, dados chegam em alta frequência. O sistema deve "
            "processar, validar e rejeitar dados inválidos sem travar o pipeline "
            "ou aceitar silenciosamente informações corrompidas."
        ),
        examples=[
            TestExample(
                name="test_ingestion_rejects_bad_schema",
                description="Garante que payload com schema inválido é rejeitado com erro descritivo.",
                file_hint="tests/ingestion/test_runtime.py",
            ),
        ],
        status="planned",
    ),
    TestCategory(
        id="workflow_and_review",
        title="Workflow and Review",
        what_it_validates=(
            "Valida os workflows de orquestração: sequência de agentes, geração "
            "de DecisionReport, registro de feedback humano e rastreabilidade "
            "de cada recomendação até sua evidência."
        ),
        why_it_matters=(
            "O workflow é onde a análise se transforma em recomendação. Cada "
            "recomendação deve ter evidência rastreável e o feedback humano deve "
            "ser registrado para calibração contínua do sistema."
        ),
        examples=[
            TestExample(
                name="test_workflow_generates_report",
                description="Garante que o workflow completo gera um DecisionReport com todos os campos.",
                file_hint="tests/workflow/test_workflow.py",
            ),
            TestExample(
                name="test_human_feedback_recorded",
                description="Garante que o feedback humano é persistido e associado ao run correto.",
                file_hint="tests/workflow/test_feedback.py",
            ),
        ],
        status="planned",
    ),
    TestCategory(
        id="governance_and_observability",
        title="Governance and Observability",
        what_it_validates=(
            "Valida os mecanismos de governança: logs de auditoria, rastreabilidade "
            "de decisões, alertas de qualidade de dados e relatórios de confiança."
        ),
        why_it_matters=(
            "Rastreabilidade total é um princípio fundamental do sistema. Toda "
            "decisão deve ser auditável: quem recomendou, com qual evidência, "
            "com qual confiança e qual foi o resultado real."
        ),
        examples=[
            TestExample(
                name="test_audit_log_created",
                description="Garante que cada run gera entrada no log de auditoria.",
                file_hint="tests/governance/test_audit.py",
            ),
        ],
        status="planned",
    ),
    TestCategory(
        id="api_and_cli",
        title="API and CLI",
        what_it_validates=(
            "Valida os contratos da API interna e do CLI: rotas, schemas de "
            "request/response, tratamento de erros, comando football-os app e "
            "demais subcomandos."
        ),
        why_it_matters=(
            "A API e o CLI são as interfaces primárias de integração. Contratos "
            "quebrados silenciosamente podem causar falhas em cascata em pipelines "
            "automatizados e ferramentas de análise."
        ),
        examples=[
            TestExample(
                name="test_health_endpoint_returns_200",
                description="Garante que GET /health retorna 200 com status e versão.",
                file_hint="tests/web/test_routes.py",
            ),
            TestExample(
                name="test_home_page_renders",
                description="Garante que a página Home renderiza sem erros.",
                file_hint="tests/web/test_routes.py",
            ),
            TestExample(
                name="test_runs_list_page_renders",
                description="Garante que a página de lista de runs renderiza sem erros.",
                file_hint="tests/web/test_routes.py",
            ),
            TestExample(
                name="test_run_detail_page_renders",
                description="Garante que a página de detalhe de run renderiza para IDs válidos.",
                file_hint="tests/web/test_routes.py",
            ),
            TestExample(
                name="test_run_detail_404_for_unknown",
                description="Garante que run_id inexistente retorna 404 com mensagem amigável.",
                file_hint="tests/web/test_routes.py",
            ),
            TestExample(
                name="test_test_health_page_renders",
                description="Garante que a página Test Health renderiza o catálogo completo.",
                file_hint="tests/web/test_routes.py",
            ),
            TestExample(
                name="test_cli_app_command_exists",
                description="Garante que o comando football-os app está registrado no CLI.",
                file_hint="tests/cli/test_cli.py",
            ),
        ],
        status="active",
    ),
    TestCategory(
        id="pilot_evaluation",
        title="Pilot Evaluation",
        what_it_validates=(
            "Valida o ciclo completo de piloto: seleção de cenários reais, "
            "execução de workflows, coleta de feedback humano e geração de "
            "pilot report com métricas de qualidade."
        ),
        why_it_matters=(
            "O piloto é a validação final do sistema em condições próximas ao "
            "uso real. Sem avaliação sistemática do piloto, não é possível "
            "calibrar a confiança do sistema ou identificar lacunas críticas."
        ),
        examples=[
            TestExample(
                name="test_pilot_report_generated",
                description="Garante que o pilot report é gerado com métricas de qualidade e feedback.",
                file_hint="tests/pilot/test_pilot.py",
            ),
        ],
        status="planned",
    ),
]


def get_catalog() -> List[TestCategory]:
    """Retorna o catálogo completo de categorias de testes."""
    return TEST_CATALOG


def get_category(category_id: str) -> TestCategory | None:
    """Retorna uma categoria pelo ID, ou None se não encontrada."""
    for cat in TEST_CATALOG:
        if cat.id == category_id:
            return cat
    return None
