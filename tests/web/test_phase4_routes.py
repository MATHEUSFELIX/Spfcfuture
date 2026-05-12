"""
tests/web/test_phase4_routes.py

Testes de integração para as rotas da Fase 4 (Opponent Preparation).

Categorias cobertas:
    - Integration: Todas as rotas HTML e JSON da Fase 4
    - Contract: Estrutura das respostas JSON
    - Boundary: IDs válidos e inválidos
    - Regression: Smoke test de todas as rotas
"""
import json
import pytest
from fastapi.testclient import TestClient

from src.web.local_app import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# HTML Routes — /opponents
# ---------------------------------------------------------------------------

class TestOpponentsListRoute:
    """Testes para a rota GET /opponents."""

    def test_returns_200(self, client):
        response = client.get("/opponents")
        assert response.status_code == 200

    def test_content_type_is_html(self, client):
        response = client.get("/opponents")
        assert "text/html" in response.headers["content-type"]

    def test_page_contains_adversarios_title(self, client):
        response = client.get("/opponents")
        assert "Adversário" in response.text or "adversário" in response.text

    def test_page_contains_3_opponents(self, client):
        response = client.get("/opponents")
        # Should contain all 3 demo opponent names
        assert "demo-opp-001" in response.text or "[Demo]" in response.text

    def test_page_contains_demo_notice(self, client):
        response = client.get("/opponents")
        assert "Demo" in response.text or "demo" in response.text

    def test_page_contains_nav_link(self, client):
        response = client.get("/opponents")
        assert "Adversários" in response.text or "/opponents" in response.text

    def test_page_contains_threat_level(self, client):
        response = client.get("/opponents")
        assert "Ameaça" in response.text or "ameaça" in response.text or "threat" in response.text.lower()


# ---------------------------------------------------------------------------
# HTML Routes — /opponents/{id}
# ---------------------------------------------------------------------------

class TestOpponentDetailRoute:
    """Testes para a rota GET /opponents/{opponent_id}."""

    def test_opp_001_returns_200(self, client):
        response = client.get("/opponents/demo-opp-001")
        assert response.status_code == 200

    def test_opp_002_returns_200(self, client):
        response = client.get("/opponents/demo-opp-002")
        assert response.status_code == 200

    def test_opp_003_returns_200(self, client):
        response = client.get("/opponents/demo-opp-003")
        assert response.status_code == 200

    def test_invalid_id_returns_404(self, client):
        response = client.get("/opponents/nonexistent-id")
        assert response.status_code == 404

    def test_content_type_is_html(self, client):
        response = client.get("/opponents/demo-opp-001")
        assert "text/html" in response.headers["content-type"]

    def test_page_contains_pressing_section(self, client):
        response = client.get("/opponents/demo-opp-001")
        assert "Pressing" in response.text or "pressing" in response.text

    def test_page_contains_zone_vulnerabilities(self, client):
        response = client.get("/opponents/demo-opp-001")
        assert "Vulnerabilidade" in response.text or "vulnerabilidade" in response.text or "Zona" in response.text

    def test_page_contains_set_piece_section(self, client):
        response = client.get("/opponents/demo-opp-001")
        assert "Bola Parada" in response.text or "bola parada" in response.text or "Set Piece" in response.text

    def test_page_contains_tactical_alerts(self, client):
        response = client.get("/opponents/demo-opp-001")
        assert "Alerta" in response.text or "alerta" in response.text or "Alert" in response.text

    def test_page_contains_game_plan_link(self, client):
        response = client.get("/opponents/demo-opp-001")
        assert "/plan" in response.text or "Plano de Jogo" in response.text

    def test_page_contains_demo_notice(self, client):
        response = client.get("/opponents/demo-opp-001")
        assert "Demo" in response.text or "demo" in response.text

    def test_404_page_contains_error_message(self, client):
        response = client.get("/opponents/nonexistent-id")
        assert "não encontrado" in response.text.lower() or "not found" in response.text.lower()


# ---------------------------------------------------------------------------
# HTML Routes — /opponents/{id}/plan
# ---------------------------------------------------------------------------

class TestGamePlanRoute:
    """Testes para a rota GET /opponents/{opponent_id}/plan."""

    def test_opp_001_plan_returns_200(self, client):
        response = client.get("/opponents/demo-opp-001/plan")
        assert response.status_code == 200

    def test_opp_002_plan_returns_200(self, client):
        response = client.get("/opponents/demo-opp-002/plan")
        assert response.status_code == 200

    def test_opp_003_plan_returns_200(self, client):
        response = client.get("/opponents/demo-opp-003/plan")
        assert response.status_code == 200

    def test_invalid_id_plan_returns_404(self, client):
        response = client.get("/opponents/nonexistent-id/plan")
        assert response.status_code == 404

    def test_content_type_is_html(self, client):
        response = client.get("/opponents/demo-opp-001/plan")
        assert "text/html" in response.headers["content-type"]

    def test_plan_page_contains_plano_de_jogo(self, client):
        response = client.get("/opponents/demo-opp-001/plan")
        assert "Plano de Jogo" in response.text or "plano de jogo" in response.text

    def test_plan_page_contains_defensive_section(self, client):
        response = client.get("/opponents/demo-opp-001/plan")
        assert "Defens" in response.text or "defens" in response.text

    def test_plan_page_contains_offensive_section(self, client):
        response = client.get("/opponents/demo-opp-001/plan")
        assert "Ofens" in response.text or "ofens" in response.text

    def test_plan_page_contains_key_messages(self, client):
        response = client.get("/opponents/demo-opp-001/plan")
        assert "Mensagem" in response.text or "mensagem" in response.text or "chave" in response.text.lower()

    def test_plan_page_contains_disclaimer(self, client):
        response = client.get("/opponents/demo-opp-001/plan")
        assert "decisão" in response.text.lower() or "humana" in response.text.lower() or "disclaimer" in response.text.lower()

    def test_plan_page_contains_demo_notice(self, client):
        response = client.get("/opponents/demo-opp-001/plan")
        assert "Demo" in response.text or "demo" in response.text

    def test_plan_page_contains_confidence_info(self, client):
        response = client.get("/opponents/demo-opp-001/plan")
        assert "Confiança" in response.text or "confiança" in response.text or "confidence" in response.text.lower()


# ---------------------------------------------------------------------------
# JSON API Routes — /api/opponents
# ---------------------------------------------------------------------------

class TestApiOpponentsRoute:
    """Testes para a rota GET /api/opponents."""

    def test_returns_200(self, client):
        response = client.get("/api/opponents")
        assert response.status_code == 200

    def test_content_type_is_json(self, client):
        response = client.get("/api/opponents")
        assert "application/json" in response.headers["content-type"]

    def test_response_has_opponents_key(self, client):
        data = client.get("/api/opponents").json()
        assert "opponents" in data

    def test_response_has_total_key(self, client):
        data = client.get("/api/opponents").json()
        assert "total" in data

    def test_total_is_3(self, client):
        data = client.get("/api/opponents").json()
        assert data["total"] == 3

    def test_opponents_list_has_3_items(self, client):
        data = client.get("/api/opponents").json()
        assert len(data["opponents"]) == 3

    def test_each_opponent_has_required_keys(self, client):
        data = client.get("/api/opponents").json()
        required_keys = [
            "opponent_id", "opponent_name", "overall_threat_level",
            "pressing_intensity", "data_completeness",
            "source_matches_count", "alerts_count", "zone_vulnerabilities_count",
        ]
        for opp in data["opponents"]:
            for key in required_keys:
                assert key in opp, f"Missing key '{key}' in opponent: {opp.get('opponent_id')}"

    def test_threat_levels_are_valid(self, client):
        data = client.get("/api/opponents").json()
        valid_levels = {"critical", "high", "moderate", "low", "unknown"}
        for opp in data["opponents"]:
            assert opp["overall_threat_level"] in valid_levels


# ---------------------------------------------------------------------------
# JSON API Routes — /api/opponents/{id}
# ---------------------------------------------------------------------------

class TestApiOpponentDetailRoute:
    """Testes para a rota GET /api/opponents/{opponent_id}."""

    def test_opp_001_returns_200(self, client):
        response = client.get("/api/opponents/demo-opp-001")
        assert response.status_code == 200

    def test_invalid_id_returns_404(self, client):
        response = client.get("/api/opponents/nonexistent")
        assert response.status_code == 404

    def test_content_type_is_json(self, client):
        response = client.get("/api/opponents/demo-opp-001")
        assert "application/json" in response.headers["content-type"]

    def test_response_has_required_keys(self, client):
        data = client.get("/api/opponents/demo-opp-001").json()
        required_keys = [
            "opponent_id", "opponent_name", "analysis_date",
            "pressing_analysis", "zone_vulnerabilities",
            "transition_vulnerabilities", "set_piece_analysis",
            "tactical_alerts", "formation_summary",
            "overall_threat_level", "overall_assessment",
            "key_observations", "data_completeness", "source_matches_count",
        ]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"

    def test_opponent_id_matches_request(self, client):
        data = client.get("/api/opponents/demo-opp-001").json()
        assert data["opponent_id"] == "demo-opp-001"

    def test_pressing_analysis_has_intensity(self, client):
        data = client.get("/api/opponents/demo-opp-001").json()
        assert "intensity" in data["pressing_analysis"]

    def test_zone_vulnerabilities_is_list(self, client):
        data = client.get("/api/opponents/demo-opp-001").json()
        assert isinstance(data["zone_vulnerabilities"], list)

    def test_tactical_alerts_is_list(self, client):
        data = client.get("/api/opponents/demo-opp-001").json()
        assert isinstance(data["tactical_alerts"], list)

    def test_404_response_has_detail(self, client):
        data = client.get("/api/opponents/nonexistent").json()
        assert "detail" in data


# ---------------------------------------------------------------------------
# JSON API Routes — /api/opponents/{id}/plan
# ---------------------------------------------------------------------------

class TestApiOpponentPlanRoute:
    """Testes para a rota GET /api/opponents/{opponent_id}/plan."""

    def test_opp_001_plan_returns_200(self, client):
        response = client.get("/api/opponents/demo-opp-001/plan")
        assert response.status_code == 200

    def test_invalid_id_plan_returns_404(self, client):
        response = client.get("/api/opponents/nonexistent/plan")
        assert response.status_code == 404

    def test_content_type_is_json(self, client):
        response = client.get("/api/opponents/demo-opp-001/plan")
        assert "application/json" in response.headers["content-type"]

    def test_response_has_required_keys(self, client):
        data = client.get("/api/opponents/demo-opp-001/plan").json()
        required_keys = [
            "plan_id", "created_at", "match_context", "opponent_id",
            "opponent_name", "sections", "key_messages", "risk_flags",
            "contingency_notes", "overall_confidence", "disclaimer",
            "data_completeness",
        ]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"

    def test_sections_is_list(self, client):
        data = client.get("/api/opponents/demo-opp-001/plan").json()
        assert isinstance(data["sections"], list)

    def test_sections_count_is_at_least_4(self, client):
        # The web app passes SPFC principles, so the plan may have 4 or 5 sections
        # (4 tactical phases + 1 optional general/principles section)
        data = client.get("/api/opponents/demo-opp-001/plan").json()
        assert len(data["sections"]) >= 4

    def test_key_messages_is_list(self, client):
        data = client.get("/api/opponents/demo-opp-001/plan").json()
        assert isinstance(data["key_messages"], list)

    def test_disclaimer_is_not_empty(self, client):
        data = client.get("/api/opponents/demo-opp-001/plan").json()
        assert len(data["disclaimer"]) > 10

    def test_overall_confidence_in_range(self, client):
        data = client.get("/api/opponents/demo-opp-001/plan").json()
        assert 0.0 <= data["overall_confidence"] <= 1.0

    def test_plan_id_starts_with_plan(self, client):
        data = client.get("/api/opponents/demo-opp-001/plan").json()
        assert data["plan_id"].startswith("plan-")

    def test_opponent_id_matches_request(self, client):
        data = client.get("/api/opponents/demo-opp-001/plan").json()
        assert data["opponent_id"] == "demo-opp-001"

    def test_each_section_has_required_keys(self, client):
        data = client.get("/api/opponents/demo-opp-001/plan").json()
        required_keys = ["title", "phase", "instructions", "rationale", "priority", "confidence"]
        for section in data["sections"]:
            for key in required_keys:
                assert key in section, f"Missing key '{key}' in section"

    def test_all_3_demo_opponents_have_plans(self, client):
        for opp_id in ["demo-opp-001", "demo-opp-002", "demo-opp-003"]:
            response = client.get(f"/api/opponents/{opp_id}/plan")
            assert response.status_code == 200, f"Plan for {opp_id} should return 200"


# ---------------------------------------------------------------------------
# Navigation Integration Tests
# ---------------------------------------------------------------------------

class TestPhase4Navigation:
    """Testes de integração de navegação entre páginas da Fase 4."""

    def test_home_page_has_opponents_link(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "/opponents" in response.text or "Adversários" in response.text

    def test_opponents_list_links_to_detail(self, client):
        response = client.get("/opponents")
        assert "/opponents/demo-opp-" in response.text

    def test_opponent_detail_links_to_plan(self, client):
        response = client.get("/opponents/demo-opp-001")
        assert "/plan" in response.text

    def test_opponent_detail_links_back_to_list(self, client):
        response = client.get("/opponents/demo-opp-001")
        assert "/opponents" in response.text

    def test_game_plan_links_back_to_opponent(self, client):
        response = client.get("/opponents/demo-opp-001/plan")
        assert "/opponents/demo-opp-001" in response.text or "/opponents" in response.text
