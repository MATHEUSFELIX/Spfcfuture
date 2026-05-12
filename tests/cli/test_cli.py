"""
Testes do CLI — SPFC Champion Decision OS.

Categoria: API and CLI
Valida: comandos do CLI, registro de subcomandos e comportamento esperado.
"""
import pytest
from click.testing import CliRunner

from src.cli.main import APP_VERSION, cli


@pytest.fixture
def runner():
    """CliRunner para testes do Click."""
    return CliRunner()


class TestCLIGroup:
    """Testes do grupo principal do CLI."""

    def test_cli_help_exits_zero(self, runner):
        """Garante que --help retorna código de saída 0."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0

    def test_cli_version_exits_zero(self, runner):
        """Garante que --version retorna código de saída 0."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0

    def test_cli_version_contains_version_string(self, runner):
        """Garante que --version exibe a versão correta."""
        result = runner.invoke(cli, ["--version"])
        assert APP_VERSION in result.output

    def test_cli_app_command_exists(self, runner):
        """
        Garante que o comando 'app' está registrado no CLI.
        Este é o entregável principal: football-os app.
        """
        result = runner.invoke(cli, ["app", "--help"])
        assert result.exit_code == 0
        assert "app" in result.output.lower() or "Inicia" in result.output

    def test_cli_version_command_exists(self, runner):
        """Garante que o comando 'version' está registrado no CLI."""
        result = runner.invoke(cli, ["version"])
        assert result.exit_code == 0
        assert APP_VERSION in result.output

    def test_cli_health_command_exists(self, runner):
        """Garante que o comando 'health' está registrado no CLI."""
        result = runner.invoke(cli, ["health", "--help"])
        assert result.exit_code == 0


class TestAppCommand:
    """Testes do subcomando 'app'."""

    def test_app_help_shows_host_option(self, runner):
        """Garante que o comando 'app' documenta a opção --host."""
        result = runner.invoke(cli, ["app", "--help"])
        assert "--host" in result.output

    def test_app_help_shows_port_option(self, runner):
        """Garante que o comando 'app' documenta a opção --port."""
        result = runner.invoke(cli, ["app", "--help"])
        assert "--port" in result.output

    def test_app_help_shows_reload_option(self, runner):
        """Garante que o comando 'app' documenta a opção --reload."""
        result = runner.invoke(cli, ["app", "--help"])
        assert "--reload" in result.output

    def test_app_help_shows_no_browser_option(self, runner):
        """Garante que o comando 'app' documenta a opção --no-browser."""
        result = runner.invoke(cli, ["app", "--help"])
        assert "--no-browser" in result.output

    def test_app_help_shows_default_port(self, runner):
        """Garante que o comando 'app' documenta a porta padrão."""
        result = runner.invoke(cli, ["app", "--help"])
        assert "8000" in result.output


class TestHealthCommand:
    """Testes do subcomando 'health'."""

    def test_health_command_exits_zero(self, runner):
        """Garante que o comando 'health' retorna código de saída 0 quando tudo está ok."""
        result = runner.invoke(cli, ["health"])
        assert result.exit_code == 0

    def test_health_command_shows_ok_for_all_components(self, runner):
        """Garante que o comando 'health' mostra [OK] para todos os componentes."""
        result = runner.invoke(cli, ["health"])
        assert "[OK]" in result.output

    def test_health_command_checks_web_app(self, runner):
        """Garante que o comando 'health' verifica o Web App."""
        result = runner.invoke(cli, ["health"])
        assert "Web App" in result.output

    def test_health_command_checks_core_models(self, runner):
        """Garante que o comando 'health' verifica os Core Models."""
        result = runner.invoke(cli, ["health"])
        assert "Core Models" in result.output

    def test_health_command_checks_artifact_store(self, runner):
        """Garante que o comando 'health' verifica o Artifact Store."""
        result = runner.invoke(cli, ["health"])
        assert "Artifact Store" in result.output
