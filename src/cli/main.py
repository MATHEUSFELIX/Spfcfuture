"""
CLI — SPFC Champion Decision OS.

Ponto de entrada principal do sistema via linha de comando.

Uso:
    football-os app              # Inicia o web app local
    football-os app --port 8080  # Inicia na porta 8080
    football-os app --host 0.0.0.0  # Expõe na rede local
    football-os version          # Exibe versão
    football-os health           # Verifica saúde do sistema
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click

APP_VERSION = "0.1.0"
APP_NAME = "SPFC Champion Decision OS"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


@click.group()
@click.version_option(version=APP_VERSION, prog_name="football-os")
def cli() -> None:
    """
    SPFC Champion Decision OS — Sistema de Apoio a Decisões Esportivas do São Paulo FC.

    \b
    Princípios:
      - Assistente, não oráculo.
      - Evidência acima de narrativa.
      - Decisão final é humana.
    """


@cli.command(name="app")
@click.option(
    "--host",
    default=DEFAULT_HOST,
    show_default=True,
    help="Host para o servidor web.",
)
@click.option(
    "--port",
    default=DEFAULT_PORT,
    show_default=True,
    type=int,
    help="Porta para o servidor web.",
)
@click.option(
    "--reload",
    is_flag=True,
    default=False,
    help="Ativa hot-reload para desenvolvimento.",
)
@click.option(
    "--no-browser",
    is_flag=True,
    default=False,
    help="Não abre o navegador automaticamente.",
)
def app_command(host: str, port: int, reload: bool, no_browser: bool) -> None:
    """
    Inicia o web app local do SPFC Champion Decision OS.

    \b
    O servidor web é iniciado em http://{host}:{port}
    Pressione Ctrl+C para parar.
    """
    url = f"http://{host}:{port}"
    click.echo(f"\n{'='*60}")
    click.echo(f"  {APP_NAME}")
    click.echo(f"  Versão: {APP_VERSION}")
    click.echo(f"{'='*60}")
    click.echo(f"\n  Servidor: {url}")
    click.echo(f"  API Docs: {url}/api/docs")
    click.echo(f"  Healthcheck: {url}/health")
    click.echo(f"  Test Health: {url}/test-health")
    click.echo(f"\n  Pressione Ctrl+C para parar.\n")

    if not no_browser:
        _try_open_browser(url)

    import uvicorn
    uvicorn.run(
        "src.web.local_app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


@cli.command(name="version")
def version_command() -> None:
    """Exibe a versão do sistema."""
    click.echo(f"{APP_NAME} v{APP_VERSION}")


@cli.command(name="health")
def health_command() -> None:
    """
    Verifica a saúde do sistema (sem iniciar o servidor web).
    Testa importações e dependências críticas.
    """
    click.echo(f"\n{APP_NAME} — Health Check\n")
    errors = []

    checks = [
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("Jinja2", "jinja2"),
        ("Click", "click"),
        ("Core Models", "src.core.models"),
        ("Artifact Store", "src.core.artifact_store"),
        ("Test Catalog", "src.core.test_catalog"),
        ("Web App", "src.web.local_app"),
    ]

    for label, module in checks:
        try:
            __import__(module)
            click.echo(f"  [OK] {label}")
        except ImportError as exc:
            click.echo(f"  [FAIL] {label}: {exc}", err=True)
            errors.append(label)

    if errors:
        click.echo(f"\n  {len(errors)} verificação(ões) falharam: {', '.join(errors)}")
        click.echo("  Execute: pip install -r requirements.txt")
        sys.exit(1)
    else:
        click.echo(f"\n  Todos os componentes estão operacionais.")


def _try_open_browser(url: str) -> None:
    """Tenta abrir o navegador padrão na URL do app."""
    import webbrowser
    try:
        webbrowser.open(url)
    except Exception:
        pass  # Falha silenciosa — o servidor ainda inicia normalmente


if __name__ == "__main__":
    cli()
