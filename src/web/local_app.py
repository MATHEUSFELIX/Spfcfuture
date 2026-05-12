"""
Local Web App — SPFC Champion Decision OS.

Interface web local para visualização de runs, healthcheck e catálogo de testes.

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

# ---------------------------------------------------------------------------
# Configuração do App
# ---------------------------------------------------------------------------

APP_VERSION = "0.1.0"
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
# Rotas HTML
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
# Rotas JSON (API)
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
