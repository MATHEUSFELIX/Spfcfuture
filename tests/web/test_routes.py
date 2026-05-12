"""
Testes das Rotas Web — SPFC Champion Decision OS.

Categoria: API and CLI
Valida: todas as rotas do web app (HTML e JSON), status codes, conteúdo e erros.
"""
import json

import pytest
from fastapi.testclient import TestClient

from src.web.local_app import APP_TITLE, APP_VERSION, app

client = TestClient(app)


class TestHomeRoute:
    """Testes da rota GET /"""

    def test_home_returns_200(self):
        """Garante que a página Home retorna status 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_home_returns_html(self):
        """Garante que a página Home retorna HTML."""
        response = client.get("/")
        assert "text/html" in response.headers["content-type"]

    def test_home_contains_app_title(self):
        """Garante que a página Home contém o título do sistema."""
        response = client.get("/")
        assert APP_TITLE in response.text

    def test_home_contains_navigation_links(self):
        """Garante que a página Home contém links de navegação essenciais."""
        response = client.get("/")
        assert "/runs" in response.text
        assert "/test-health" in response.text
        assert "/health" in response.text

    def test_home_contains_principles_section(self):
        """Garante que a página Home exibe os princípios do sistema."""
        response = client.get("/")
        # Princípio 3: Não inventar dados
        assert "Não inventar dados" in response.text

    def test_home_contains_modules_section(self):
        """Garante que a página Home exibe os módulos do sistema."""
        response = client.get("/")
        assert "Match Intelligence" in response.text
        assert "Squad Intelligence" in response.text

    def test_home_contains_footer_disclaimer(self):
        """
        Garante que a Home exibe o disclaimer de que a decisão final é humana.
        Princípio 8: Decisão final é humana.
        """
        response = client.get("/")
        assert "Decisão final" in response.text or "decisão final" in response.text


class TestRunsListRoute:
    """Testes da rota GET /runs"""

    def test_runs_returns_200(self):
        """Garante que a página de lista de runs retorna status 200."""
        response = client.get("/runs")
        assert response.status_code == 200

    def test_runs_returns_html(self):
        """Garante que a página de runs retorna HTML."""
        response = client.get("/runs")
        assert "text/html" in response.headers["content-type"]

    def test_runs_contains_demo_runs(self):
        """Garante que a página de runs exibe as runs de demonstração."""
        response = client.get("/runs")
        assert "demo-001" in response.text or "Demo" in response.text

    def test_runs_contains_fixture_tag(self):
        """Garante que as runs de demo são identificadas com a tag 'fixture'."""
        response = client.get("/runs")
        assert "fixture" in response.text

    def test_runs_page_has_table(self):
        """Garante que a página de runs tem uma tabela de listagem."""
        response = client.get("/runs")
        assert "<table" in response.text


class TestRunDetailRoute:
    """Testes da rota GET /runs/{run_id}"""

    def test_demo_run_detail_returns_200(self):
        """Garante que o detalhe de uma run de demo retorna status 200."""
        response = client.get("/runs/demo-001")
        assert response.status_code == 200

    def test_demo_run_detail_returns_html(self):
        """Garante que o detalhe de run retorna HTML."""
        response = client.get("/runs/demo-001")
        assert "text/html" in response.headers["content-type"]

    def test_demo_run_detail_contains_explanation(self):
        """
        Garante que o detalhe da run exibe a explicação.
        Princípio: Explicabilidade obrigatória.
        """
        response = client.get("/runs/demo-001")
        assert "Explicação" in response.text or "explicação" in response.text

    def test_demo_run_detail_contains_risks(self):
        """Garante que o detalhe da run exibe os riscos identificados."""
        response = client.get("/runs/demo-001")
        assert "Riscos" in response.text or "risco" in response.text.lower()

    def test_demo_run_detail_contains_metadata(self):
        """Garante que o detalhe da run exibe os metadados (run_id, módulo, status)."""
        response = client.get("/runs/demo-001")
        assert "demo-001" in response.text
        assert "match_intelligence" in response.text

    def test_unknown_run_returns_404(self):
        """Garante que run_id inexistente retorna status 404."""
        response = client.get("/runs/run-id-que-nao-existe-xyz-999")
        assert response.status_code == 404

    def test_unknown_run_404_has_friendly_message(self):
        """
        Garante que o erro 404 exibe mensagem amigável, não stack trace.
        Princípio de UX: Não mostrar stack trace cru para o usuário.
        """
        response = client.get("/runs/run-id-que-nao-existe-xyz-999")
        assert "Traceback" not in response.text
        assert "Exception" not in response.text
        # Deve conter mensagem amigável
        assert "não encontrada" in response.text.lower() or "not found" in response.text.lower()

    def test_unknown_run_404_has_action_suggestion(self):
        """Garante que o erro 404 sugere uma ação ao usuário."""
        response = client.get("/runs/run-id-que-nao-existe-xyz-999")
        assert "Ação sugerida" in response.text or "ação" in response.text.lower()

    def test_all_demo_runs_accessible(self):
        """Garante que todos os IDs de demo são acessíveis."""
        for run_id in ["demo-001", "demo-002", "demo-003"]:
            response = client.get(f"/runs/{run_id}")
            assert response.status_code == 200, (
                f"Run '{run_id}' deveria retornar 200, retornou {response.status_code}"
            )


class TestHealthRoute:
    """Testes da rota GET /health"""

    def test_health_returns_200(self):
        """Garante que o healthcheck retorna status 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self):
        """Garante que o healthcheck retorna JSON."""
        response = client.get("/health")
        assert "application/json" in response.headers["content-type"]

    def test_health_has_status_ok(self):
        """Garante que o healthcheck retorna status 'ok'."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_has_version(self):
        """Garante que o healthcheck retorna a versão do sistema."""
        response = client.get("/health")
        data = response.json()
        assert data["version"] == APP_VERSION

    def test_health_has_timestamp(self):
        """Garante que o healthcheck retorna um timestamp."""
        response = client.get("/health")
        data = response.json()
        assert "timestamp" in data
        assert data["timestamp"].endswith("Z")

    def test_health_has_app_name(self):
        """Garante que o healthcheck retorna o nome do sistema."""
        response = client.get("/health")
        data = response.json()
        assert data["app"] == APP_TITLE


class TestTestHealthRoute:
    """Testes da rota GET /test-health"""

    def test_test_health_returns_200(self):
        """Garante que a página Test Health retorna status 200."""
        response = client.get("/test-health")
        assert response.status_code == 200

    def test_test_health_returns_html(self):
        """Garante que a página Test Health retorna HTML."""
        response = client.get("/test-health")
        assert "text/html" in response.headers["content-type"]

    def test_test_health_contains_all_categories(self):
        """Garante que a página Test Health exibe todas as 10 categorias."""
        response = client.get("/test-health")
        expected_titles = [
            "Domain Models",
            "Pipeline",
            "Context and Priors",
            "Viewer",
            "Video-to-State",
            "Runtime Ingestion",
            "Workflow and Review",
            "Governance and Observability",
            "API and CLI",
            "Pilot Evaluation",
        ]
        for title in expected_titles:
            assert title in response.text, (
                f"Categoria '{title}' não encontrada na página Test Health."
            )

    def test_test_health_contains_what_it_validates(self):
        """Garante que a página Test Health exibe 'O que valida' para as categorias."""
        response = client.get("/test-health")
        assert "O que valida" in response.text

    def test_test_health_contains_why_it_matters(self):
        """Garante que a página Test Health exibe 'Por que importa'."""
        response = client.get("/test-health")
        assert "Por que importa" in response.text

    def test_test_health_contains_status_summary(self):
        """Garante que a página Test Health exibe o resumo de status."""
        response = client.get("/test-health")
        assert "Ativas" in response.text or "Planejadas" in response.text


class TestAPIRoutes:
    """Testes das rotas da API JSON."""

    def test_api_health_returns_200(self):
        """Garante que GET /api/health retorna 200."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_api_runs_returns_200(self):
        """Garante que GET /api/runs retorna 200."""
        response = client.get("/api/runs")
        assert response.status_code == 200

    def test_api_runs_returns_list(self):
        """Garante que GET /api/runs retorna uma lista de runs."""
        response = client.get("/api/runs")
        data = response.json()
        assert "runs" in data
        assert isinstance(data["runs"], list)
        assert len(data["runs"]) > 0

    def test_api_run_detail_returns_200_for_demo(self):
        """Garante que GET /api/runs/demo-001 retorna 200."""
        response = client.get("/api/runs/demo-001")
        assert response.status_code == 200

    def test_api_run_detail_returns_404_for_unknown(self):
        """Garante que GET /api/runs/{id_desconhecido} retorna 404."""
        response = client.get("/api/runs/id-desconhecido-xyz-999")
        assert response.status_code == 404

    def test_api_run_detail_404_has_error_info(self):
        """Garante que o 404 da API tem informações de erro estruturadas."""
        response = client.get("/api/runs/id-desconhecido-xyz-999")
        data = response.json()
        assert "detail" in data

    def test_api_test_catalog_returns_200(self):
        """Garante que GET /api/test-catalog retorna 200."""
        response = client.get("/api/test-catalog")
        assert response.status_code == 200

    def test_api_test_catalog_has_categories(self):
        """Garante que GET /api/test-catalog retorna as categorias."""
        response = client.get("/api/test-catalog")
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) == 10

    def test_api_run_detail_has_explanation(self):
        """
        Garante que o JSON de detalhe de run tem campo 'explanation'.
        Princípio: Explicabilidade obrigatória.
        """
        response = client.get("/api/runs/demo-001")
        data = response.json()
        assert "explanation" in data
        assert data["explanation"] != ""
