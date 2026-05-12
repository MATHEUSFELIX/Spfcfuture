"""
Local Web App — SPFC Champion Decision OS.

Interface web local para visualização de runs, healthcheck, catálogo de testes,
base de conhecimento SPFC e análise de elenco.

Princípio arquitetural: UI não contém lógica tática.
Princípio de UX: Não mostrar stack trace cru — mostrar erro, causa provável,
arquivo afetado e ação sugerida.

Compatível com Starlette >= 1.0 (request como primeiro argumento do TemplateResponse).
"""
from __future__ import annotations

import platform
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.core.artifact_store import ArtifactStore
from src.core.test_catalog import get_catalog
from src.opponent_prep.game_plan import GamePlanGenerator
from src.opponent_prep.opponent_analyzer import OpponentAnalyzer as OppAnalyzer
from src.opponent_prep.opponent_fixtures import (
    build_demo_opponents,
    get_demo_opponent_by_id,
)
from src.spfc_base.knowledge_base import SPFC_KNOWLEDGE_BASE
from src.squad_intelligence.squad_analyzer import SquadAnalyzer
from src.squad_intelligence.squad_fixtures import build_demo_squad

# ---------------------------------------------------------------------------
# Configuração do App
# ---------------------------------------------------------------------------

APP_VERSION = "0.3.0"
APP_TITLE = "SPFC Champion Decision OS"
APP_DESCRIPTION = "Sistema de Apoio a Decisões Esportivas do São Paulo FC"

_BASE_DIR = Path(__file__).parent
_TEMPLATES_DIR = _BASE_DIR / "templates"
_STATIC_DIR = _BASE_DIR / "static"

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Monta arquivos estáticos
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
store = ArtifactStore()
analyzer = SquadAnalyzer()
opp_analyzer = OppAnalyzer()
plan_generator = GamePlanGenerator()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_ctx(request: Request) -> Dict[str, Any]:
    """Contexto base compartilhado por todos os templates (sem 'request')."""
    return {
        "app_title": APP_TITLE,
        "app_version": APP_VERSION,
        "current_year": datetime.utcnow().year,
    }


def _render(
    request: Request,
    template_name: str,
    context: Optional[Dict[str, Any]] = None,
    status_code: int = 200,
) -> HTMLResponse:
    """
    Renderiza um template com a API do Starlette 1.0+.
    O request é passado como primeiro argumento posicional.
    """
    ctx = _base_ctx(request)
    if context:
        ctx.update(context)
    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context=ctx,
        status_code=status_code,
    )


# ---------------------------------------------------------------------------
# Rotas HTML — Fase 1
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, summary="Home — Página inicial")
async def home(request: Request) -> HTMLResponse:
    """
    Página inicial do SPFC Champion Decision OS.
    Exibe visão geral do sistema, módulos disponíveis e acesso rápido.
    """
    runs = store.list_runs(include_demo=True)[:5]
    return _render(request, "home.html", {"runs": runs})


@app.get("/runs", response_class=HTMLResponse, summary="Lista de Runs")
async def runs_list(request: Request) -> HTMLResponse:
    """
    Lista todas as execuções (runs) do pipeline de decisão.
    Exibe status, módulo, confiança e data de cada run.
    """
    runs = store.list_runs(include_demo=True)
    return _render(request, "runs.html", {"runs": runs})


@app.get("/runs/{run_id}", response_class=HTMLResponse, summary="Detalhe de Run")
async def run_detail(request: Request, run_id: str) -> HTMLResponse:
    """
    Exibe o detalhe completo de uma run: inputs, outputs, recomendações,
    riscos, explicação e feedback humano.
    """
    detail = store.get_run(run_id)
    if detail is None:
        error_ctx = {
            "error": {
                "title": "Run não encontrada",
                "cause": f"Nenhuma run com ID '{run_id}' foi encontrada no sistema.",
                "affected": "Artifact Store",
                "action": "Verifique o ID da run na lista de runs ou aguarde a conclusão do pipeline.",
            }
        }
        return _render(request, "error.html", error_ctx, status_code=404)

    return _render(request, "run_detail.html", {"detail": detail})


@app.get("/test-health", response_class=HTMLResponse, summary="Test Health — Catálogo de Testes")
async def test_health(request: Request) -> HTMLResponse:
    """
    Página de saúde dos testes: exibe o catálogo completo de categorias de testes,
    com explicações sobre o que cada categoria valida, por que importa e exemplos.
    """
    catalog = get_catalog()
    return _render(request, "test_health.html", {"catalog": catalog})


# ---------------------------------------------------------------------------
# Rotas HTML — Fase 2: Base SPFC e Squad Intelligence
# ---------------------------------------------------------------------------

@app.get("/knowledge-base", response_class=HTMLResponse, summary="Base de Conhecimento SPFC")
async def knowledge_base(request: Request) -> HTMLResponse:
    """
    Exibe a base de conhecimento do São Paulo FC: identidade do clube,
    modelo de jogo desejado e princípios táticos de referência.
    """
    return _render(request, "knowledge_base.html", {"kb": SPFC_KNOWLEDGE_BASE})


@app.get("/squad", response_class=HTMLResponse, summary="Análise de Elenco")
async def squad(request: Request) -> HTMLResponse:
    """
    Exibe a análise do elenco: profundidade por posição, lacunas táticas,
    dependências de jogadores e curva etária.

    Utiliza elenco de demonstração (dados fictícios).
    """
    players = build_demo_squad()
    report = analyzer.analyze(
        players=players,
        team_id="spfc-demo",
        season="2025 (Demo)",
    )
    return _render(
        request,
        "squad.html",
        {"players": players, "report": report},
    )


# ---------------------------------------------------------------------------
# Rotas JSON (API) — Fase 1
# ---------------------------------------------------------------------------

@app.get("/health", response_class=JSONResponse, summary="Healthcheck da aplicação")
async def health() -> JSONResponse:
    """
    Healthcheck da aplicação web.
    Retorna status, versão, Python e timestamp.
    """
    return JSONResponse(
        content={
            "status": "ok",
            "app": APP_TITLE,
            "version": APP_VERSION,
            "python": sys.version,
            "platform": platform.system(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    )


@app.get("/api/health", response_class=JSONResponse, summary="API Healthcheck (JSON)")
async def api_health() -> JSONResponse:
    """Alias JSON para o healthcheck — útil para monitoramento programático."""
    return await health()


@app.get("/api/runs", response_class=JSONResponse, summary="API — Lista de Runs (JSON)")
async def api_runs() -> JSONResponse:
    """Retorna a lista de runs em formato JSON."""
    runs = store.list_runs(include_demo=True)
    return JSONResponse(content={"runs": [r.to_dict() for r in runs]})


@app.get("/api/runs/{run_id}", response_class=JSONResponse, summary="API — Detalhe de Run (JSON)")
async def api_run_detail(run_id: str) -> JSONResponse:
    """Retorna o detalhe de uma run em formato JSON."""
    detail = store.get_run(run_id)
    if detail is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Run não encontrada",
                "run_id": run_id,
                "action": "Verifique o ID da run na lista de runs.",
            },
        )
    return JSONResponse(content=detail.to_dict())


@app.get("/api/test-catalog", response_class=JSONResponse, summary="API — Catálogo de Testes (JSON)")
async def api_test_catalog() -> JSONResponse:
    """Retorna o catálogo de categorias de testes em formato JSON."""
    catalog = get_catalog()
    return JSONResponse(
        content={
            "categories": [
                {
                    "id": cat.id,
                    "title": cat.title,
                    "what_it_validates": cat.what_it_validates,
                    "why_it_matters": cat.why_it_matters,
                    "examples": [
                        {
                            "name": ex.name,
                            "description": ex.description,
                            "file_hint": ex.file_hint,
                        }
                        for ex in cat.examples
                    ],
                    "status": cat.status,
                    "status_label": cat.status_label,
                }
                for cat in catalog
            ]
        }
    )


# ---------------------------------------------------------------------------
# Rotas HTML — Fase 4: Opponent Preparation
# ---------------------------------------------------------------------------

@app.get("/opponents", response_class=HTMLResponse, summary="Lista de Adversários")
async def opponents_list(request: Request) -> HTMLResponse:
    """
    Lista todos os adversários analisados com resumo de ameaça,
    pressing e vulnerabilidades.
    """
    raw_opponents = build_demo_opponents()
    items = []
    for opp in raw_opponents:
        report = opp_analyzer.analyze(opp["profile"], opp["name"])
        items.append({
            "name": opp["name"],
            "description": opp["description"],
            "report": report,
        })

    critical_count = sum(
        1 for i in items
        if i["report"].overall_threat_level in ("critical", "high")
    )
    total_alerts = sum(len(i["report"].tactical_alerts) for i in items)
    total_vulnerabilities = sum(
        len(i["report"].zone_vulnerabilities) + len(i["report"].transition_vulnerabilities)
        for i in items
    )

    return _render(
        request,
        "opponents.html",
        {
            "opponents": items,
            "critical_count": critical_count,
            "total_alerts": total_alerts,
            "total_vulnerabilities": total_vulnerabilities,
            "demo_notice": True,
        },
    )


@app.get("/opponents/{opponent_id}", response_class=HTMLResponse, summary="Detalhe de Adversário")
async def opponent_detail(request: Request, opponent_id: str) -> HTMLResponse:
    """
    Exibe a análise completa de um adversário: pressing, zonas de
    vulnerabilidade, transições, bola parada e alertas táticos.
    """
    opp = get_demo_opponent_by_id(opponent_id)
    if opp is None:
        error_ctx = {
            "error": {
                "title": "Adversário não encontrado",
                "cause": f"Nenhum adversário com ID '{opponent_id}' foi encontrado.",
                "affected": "Opponent Fixtures",
                "action": "Verifique o ID do adversário na lista de adversários.",
            }
        }
        return _render(request, "error.html", error_ctx, status_code=404)

    report = opp_analyzer.analyze(opp["profile"], opp["name"])
    return _render(
        request,
        "opponent_detail.html",
        {
            "report": report,
            "opponent_name": opp["name"],
            "description": opp["description"],
            "demo_notice": True,
        },
    )


@app.get("/opponents/{opponent_id}/plan", response_class=HTMLResponse, summary="Plano de Jogo")
async def opponent_game_plan(request: Request, opponent_id: str) -> HTMLResponse:
    """
    Gera e exibe o plano de jogo pré-partida para um adversário específico.
    Combina a análise do adversário com os princípios táticos do SPFC.
    """
    opp = get_demo_opponent_by_id(opponent_id)
    if opp is None:
        error_ctx = {
            "error": {
                "title": "Adversário não encontrado",
                "cause": f"Nenhum adversário com ID '{opponent_id}' foi encontrado.",
                "affected": "Opponent Fixtures",
                "action": "Verifique o ID do adversário na lista de adversários.",
            }
        }
        return _render(request, "error.html", error_ctx, status_code=404)

    report = opp_analyzer.analyze(opp["profile"], opp["name"])
    principles = SPFC_KNOWLEDGE_BASE.game_model.non_negotiables or []
    plan = plan_generator.generate(
        analysis=report,
        spfc_principles=principles,
    )
    return _render(
        request,
        "game_plan.html",
        {"plan": plan, "demo_notice": True},
    )


# ---------------------------------------------------------------------------
# Rotas JSON (API) — Fase 2
# ---------------------------------------------------------------------------

@app.get("/api/knowledge-base", response_class=JSONResponse, summary="API — Base de Conhecimento (JSON)")
async def api_knowledge_base() -> JSONResponse:
    """Retorna a base de conhecimento do SPFC em formato JSON."""
    return JSONResponse(content=SPFC_KNOWLEDGE_BASE.to_dict())


@app.get("/api/squad", response_class=JSONResponse, summary="API — Análise de Elenco (JSON)")
async def api_squad() -> JSONResponse:
    """Retorna a análise do elenco de demonstração em formato JSON."""
    players = build_demo_squad()
    report = analyzer.analyze(
        players=players,
        team_id="spfc-demo",
        season="2025 (Demo)",
    )
    return JSONResponse(
        content={
            "players": [p.to_dict() for p in players],
            "report": report.to_dict(),
        }
    )


@app.get("/api/squad/gaps", response_class=JSONResponse, summary="API — Lacunas do Elenco (JSON)")
async def api_squad_gaps() -> JSONResponse:
    """Retorna apenas as lacunas identificadas no elenco de demonstração."""
    players = build_demo_squad()
    report = analyzer.analyze(players=players, team_id="spfc-demo", season="2025 (Demo)")
    gaps = [g.to_dict() for g in report.gap_analysis if g.gap_severity != "none"]
    return JSONResponse(
        content={
            "gaps": gaps,
            "total_gaps": len(gaps),
            "critical": sum(1 for g in report.gap_analysis if g.gap_severity == "critical"),
            "moderate": sum(1 for g in report.gap_analysis if g.gap_severity == "moderate"),
        }
    )


# ---------------------------------------------------------------------------
# Rotas JSON (API) — Fase 4: Opponent Preparation
# ---------------------------------------------------------------------------

@app.get("/api/opponents", response_class=JSONResponse, summary="API — Lista de Adversários (JSON)")
async def api_opponents() -> JSONResponse:
    """Retorna a lista de adversários analisados em formato JSON."""
    raw_opponents = build_demo_opponents()
    items = []
    for opp in raw_opponents:
        report = opp_analyzer.analyze(opp["profile"], opp["name"])
        items.append({
            "opponent_id": report.opponent_id,
            "opponent_name": report.opponent_name,
            "overall_threat_level": report.overall_threat_level,
            "pressing_intensity": report.pressing_analysis.intensity,
            "data_completeness": report.data_completeness,
            "source_matches_count": report.source_matches_count,
            "alerts_count": len(report.tactical_alerts),
            "zone_vulnerabilities_count": len(report.zone_vulnerabilities),
        })
    return JSONResponse(content={"opponents": items, "total": len(items)})


@app.get("/api/opponents/{opponent_id}", response_class=JSONResponse, summary="API — Análise de Adversário (JSON)")
async def api_opponent_detail(opponent_id: str) -> JSONResponse:
    """Retorna a análise completa de um adversário em formato JSON."""
    opp = get_demo_opponent_by_id(opponent_id)
    if opp is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Adversário não encontrado",
                "opponent_id": opponent_id,
                "action": "Verifique o ID na lista de adversários.",
            },
        )
    report = opp_analyzer.analyze(opp["profile"], opp["name"])
    return JSONResponse(content=report.to_dict())


@app.get("/api/opponents/{opponent_id}/plan", response_class=JSONResponse, summary="API — Plano de Jogo (JSON)")
async def api_opponent_plan(opponent_id: str) -> JSONResponse:
    """Retorna o plano de jogo pré-partida de um adversário em formato JSON."""
    opp = get_demo_opponent_by_id(opponent_id)
    if opp is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Adversário não encontrado",
                "opponent_id": opponent_id,
                "action": "Verifique o ID na lista de adversários.",
            },
        )
    report = opp_analyzer.analyze(opp["profile"], opp["name"])
    principles = SPFC_KNOWLEDGE_BASE.game_model.non_negotiables or []
    plan = plan_generator.generate(analysis=report, spfc_principles=principles)
    return JSONResponse(content=plan.to_dict())
