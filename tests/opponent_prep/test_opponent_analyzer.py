"""
tests/opponent_prep/test_opponent_analyzer.py

Testes para o módulo opponent_analyzer.

Categorias cobertas:
    - Unit: OpponentAnalyzer com dados completos e parciais
    - Contract: Campos obrigatórios no relatório
    - Boundary: Perfis com dados ausentes ou mínimos
    - Invariant: Confiança sempre entre 0.0 e 1.0
    - Regression: Smoke test com todos os fixtures de demo
"""
import pytest

from src.core.football_models import OpponentProfile, SetPieceProfile
from src.opponent_prep.opponent_analyzer import (
    OpponentAnalyzer,
    OpponentAnalysisReport,
    PressingAnalysis,
    ZoneVulnerability,
    TransitionVulnerability,
    SetPieceAnalysis,
    TacticalAlert,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def analyzer():
    return OpponentAnalyzer()


@pytest.fixture
def full_profile():
    """Perfil completo com todos os campos preenchidos."""
    return OpponentProfile(
        opponent_id="test-opp-full",
        formation_patterns=["4-3-3", "4-2-3-1"],
        pressing_profile="high intensity pressing with high defensive line.",
        weak_zones=[
            "Espaço nas costas da linha defensiva alta (critical)",
            "Corredor direito (right) vulnerável",
        ],
        transition_vulnerabilities=[
            "Transição defensiva após perda no campo ofensivo (alta severidade).",
        ],
        set_piece_profile=SetPieceProfile(
            corners_routine="Escanteios curtos",
            free_kick_routine="Faltas diretas",
            defensive_set_piece="Marcação por zona",
            key_takers=["Jogador 10"],
            key_targets=["Jogador 9"],
            notes="Teste",
        ),
        source_matches=["m001", "m002", "m003"],
        last_updated="2025-01-01",
    )


@pytest.fixture
def empty_profile():
    """Perfil mínimo com apenas o ID."""
    return OpponentProfile(opponent_id="test-opp-empty")


@pytest.fixture
def medium_pressing_profile():
    """Perfil com pressing médio."""
    return OpponentProfile(
        opponent_id="test-opp-medium",
        pressing_profile="medium intensity pressing with medium defensive line.",
        formation_patterns=["4-4-2"],
        source_matches=["m001", "m002"],
    )


@pytest.fixture
def low_pressing_profile():
    """Perfil com pressing baixo."""
    return OpponentProfile(
        opponent_id="test-opp-low",
        pressing_profile="low intensity pressing with low defensive line.",
        formation_patterns=["5-4-1"],
    )


# ---------------------------------------------------------------------------
# Unit Tests — OpponentAnalyzer.analyze()
# ---------------------------------------------------------------------------

class TestOpponentAnalyzerAnalyze:
    """Testes unitários do método analyze()."""

    def test_returns_report_instance(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile, "Test Opponent")
        assert isinstance(report, OpponentAnalysisReport)

    def test_report_has_correct_opponent_id(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile, "Test Opponent")
        assert report.opponent_id == "test-opp-full"

    def test_report_has_correct_opponent_name(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile, "Test Opponent")
        assert report.opponent_name == "Test Opponent"

    def test_report_has_analysis_date(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile, "Test Opponent")
        assert report.analysis_date is not None
        assert len(report.analysis_date) == 10  # YYYY-MM-DD

    def test_full_profile_has_high_pressing(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert report.pressing_analysis.intensity == "high"

    def test_medium_pressing_detected(self, analyzer, medium_pressing_profile):
        report = analyzer.analyze(medium_pressing_profile)
        assert report.pressing_analysis.intensity == "medium"

    def test_low_pressing_detected(self, analyzer, low_pressing_profile):
        report = analyzer.analyze(low_pressing_profile)
        assert report.pressing_analysis.intensity == "low"

    def test_empty_profile_has_unknown_pressing(self, analyzer, empty_profile):
        report = analyzer.analyze(empty_profile)
        assert report.pressing_analysis.intensity == "unknown"

    def test_zone_vulnerabilities_from_weak_zones(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert len(report.zone_vulnerabilities) == 2

    def test_transition_vulnerabilities_from_profile(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert len(report.transition_vulnerabilities) == 1

    def test_empty_profile_has_no_zone_vulnerabilities(self, analyzer, empty_profile):
        report = analyzer.analyze(empty_profile)
        assert report.zone_vulnerabilities == []

    def test_empty_profile_has_no_transition_vulnerabilities(self, analyzer, empty_profile):
        report = analyzer.analyze(empty_profile)
        assert report.transition_vulnerabilities == []

    def test_source_matches_count_correct(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert report.source_matches_count == 3

    def test_formation_summary_with_multiple_formations(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert "4-3-3" in report.formation_summary

    def test_formation_summary_empty_profile(self, analyzer, empty_profile):
        report = analyzer.analyze(empty_profile)
        assert "não identificada" in report.formation_summary.lower() or "insuficientes" in report.formation_summary.lower()

    def test_overall_assessment_not_empty(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert len(report.overall_assessment) > 20

    def test_key_observations_max_5(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert len(report.key_observations) <= 5


# ---------------------------------------------------------------------------
# Unit Tests — PressingAnalysis
# ---------------------------------------------------------------------------

class TestPressingAnalysis:
    """Testes para a análise de pressing."""

    def test_high_pressing_has_trigger_zones(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert len(report.pressing_analysis.trigger_zones) > 0

    def test_high_pressing_has_explanation(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert len(report.pressing_analysis.explanation) > 10

    def test_high_pressing_has_vulnerability_to_buildup(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert len(report.pressing_analysis.vulnerability_to_buildup) > 10

    def test_high_pressing_compactness_is_alto(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert report.pressing_analysis.compactness == "alto"

    def test_medium_pressing_compactness_is_medio(self, analyzer, medium_pressing_profile):
        report = analyzer.analyze(medium_pressing_profile)
        assert report.pressing_analysis.compactness == "médio"

    def test_low_pressing_compactness_is_baixo(self, analyzer, low_pressing_profile):
        report = analyzer.analyze(low_pressing_profile)
        assert report.pressing_analysis.compactness == "baixo"

    def test_pressing_to_dict_has_required_keys(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        d = report.pressing_analysis.to_dict()
        required = ["intensity", "trigger_zones", "defensive_line", "compactness",
                    "recovery_speed", "vulnerability_to_buildup", "explanation", "confidence"]
        for key in required:
            assert key in d, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# Unit Tests — ZoneVulnerability
# ---------------------------------------------------------------------------

class TestZoneVulnerabilities:
    """Testes para as vulnerabilidades de zona."""

    def test_critical_zone_detected(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        severities = [z.severity for z in report.zone_vulnerabilities]
        assert "critical" in severities

    def test_right_corridor_detected(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        corridors = [z.corridor for z in report.zone_vulnerabilities]
        assert "right" in corridors

    def test_zone_has_exploitation_method(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        for zone in report.zone_vulnerabilities:
            assert len(zone.exploitation_method) > 5

    def test_zone_to_dict_has_required_keys(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        for zone in report.zone_vulnerabilities:
            d = zone.to_dict()
            required = ["zone", "corridor", "severity", "description",
                        "exploitation_method", "evidence", "confidence"]
            for key in required:
                assert key in d, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# Unit Tests — TransitionVulnerability
# ---------------------------------------------------------------------------

class TestTransitionVulnerabilities:
    """Testes para as vulnerabilidades em transição."""

    def test_defensive_transition_detected(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        types = [t.type for t in report.transition_vulnerabilities]
        assert "defensive_transition" in types

    def test_transition_has_trigger(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        for tv in report.transition_vulnerabilities:
            assert len(tv.trigger) > 5

    def test_transition_has_exploitation_window(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        for tv in report.transition_vulnerabilities:
            assert len(tv.exploitation_window) > 5

    def test_transition_to_dict_has_required_keys(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        for tv in report.transition_vulnerabilities:
            d = tv.to_dict()
            required = ["type", "description", "trigger", "exploitation_window",
                        "key_players_involved", "severity", "confidence"]
            for key in required:
                assert key in d, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# Unit Tests — SetPieceAnalysis
# ---------------------------------------------------------------------------

class TestSetPieceAnalysis:
    """Testes para a análise de bola parada."""

    def test_offensive_threats_detected(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert len(report.set_piece_analysis.offensive_threats) > 0

    def test_key_takers_assessment_not_empty(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert len(report.set_piece_analysis.key_takers_assessment) > 10

    def test_key_targets_assessment_not_empty(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert len(report.set_piece_analysis.key_targets_assessment) > 10

    def test_defensive_setup_recommended(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert len(report.set_piece_analysis.recommended_defensive_setup) > 10

    def test_empty_set_piece_has_low_confidence(self, analyzer, empty_profile):
        report = analyzer.analyze(empty_profile)
        assert report.set_piece_analysis.confidence <= 0.2

    def test_set_piece_to_dict_has_required_keys(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        d = report.set_piece_analysis.to_dict()
        required = ["offensive_threats", "defensive_weaknesses", "key_takers_assessment",
                    "key_targets_assessment", "recommended_defensive_setup",
                    "recommended_offensive_approach", "confidence"]
        for key in required:
            assert key in d, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# Unit Tests — TacticalAlerts
# ---------------------------------------------------------------------------

class TestTacticalAlerts:
    """Testes para os alertas táticos."""

    def test_high_pressing_generates_alert(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        categories = [a.category for a in report.tactical_alerts]
        assert "pressing" in categories

    def test_set_piece_takers_generate_alert(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        categories = [a.category for a in report.tactical_alerts]
        assert "set_piece" in categories

    def test_alert_has_action_required(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        for alert in report.tactical_alerts:
            assert len(alert.action_required) > 5

    def test_alert_to_dict_has_required_keys(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        for alert in report.tactical_alerts:
            d = alert.to_dict()
            required = ["alert_id", "category", "severity", "title",
                        "description", "action_required"]
            for key in required:
                assert key in d, f"Missing key: {key}"

    def test_empty_profile_generates_no_pressing_alert(self, analyzer, empty_profile):
        report = analyzer.analyze(empty_profile)
        pressing_alerts = [a for a in report.tactical_alerts if a.category == "pressing"]
        assert len(pressing_alerts) == 0


# ---------------------------------------------------------------------------
# Invariant Tests — Confidence always between 0.0 and 1.0
# ---------------------------------------------------------------------------

class TestConfidenceInvariant:
    """Invariante: confiança sempre entre 0.0 e 1.0."""

    def test_pressing_confidence_in_range(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert 0.0 <= report.pressing_analysis.confidence <= 1.0

    def test_zone_confidence_in_range(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        for zone in report.zone_vulnerabilities:
            assert 0.0 <= zone.confidence <= 1.0, f"Zone confidence out of range: {zone.confidence}"

    def test_transition_confidence_in_range(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        for tv in report.transition_vulnerabilities:
            assert 0.0 <= tv.confidence <= 1.0, f"Transition confidence out of range: {tv.confidence}"

    def test_set_piece_confidence_in_range(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert 0.0 <= report.set_piece_analysis.confidence <= 1.0

    def test_empty_profile_pressing_confidence_in_range(self, analyzer, empty_profile):
        report = analyzer.analyze(empty_profile)
        assert 0.0 <= report.pressing_analysis.confidence <= 1.0


# ---------------------------------------------------------------------------
# Boundary Tests — Data completeness
# ---------------------------------------------------------------------------

class TestDataCompleteness:
    """Testes de completude dos dados."""

    def test_full_profile_has_high_completeness(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert report.data_completeness >= 0.8

    def test_empty_profile_has_low_completeness(self, analyzer, empty_profile):
        report = analyzer.analyze(empty_profile)
        assert report.data_completeness <= 0.2

    def test_completeness_between_0_and_1(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        assert 0.0 <= report.data_completeness <= 1.0

    def test_empty_completeness_between_0_and_1(self, analyzer, empty_profile):
        report = analyzer.analyze(empty_profile)
        assert 0.0 <= report.data_completeness <= 1.0


# ---------------------------------------------------------------------------
# Contract Tests — to_dict() structure
# ---------------------------------------------------------------------------

class TestReportToDict:
    """Testes de contrato: to_dict() retorna estrutura correta."""

    def test_report_to_dict_has_required_keys(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        d = report.to_dict()
        required = [
            "opponent_id", "opponent_name", "analysis_date",
            "pressing_analysis", "zone_vulnerabilities",
            "transition_vulnerabilities", "set_piece_analysis",
            "tactical_alerts", "formation_summary",
            "overall_threat_level", "overall_assessment",
            "key_observations", "data_completeness", "source_matches_count",
        ]
        for key in required:
            assert key in d, f"Missing key in report.to_dict(): {key}"

    def test_report_to_dict_is_json_serializable(self, analyzer, full_profile):
        import json
        report = analyzer.analyze(full_profile)
        d = report.to_dict()
        # Should not raise
        json_str = json.dumps(d)
        assert len(json_str) > 100

    def test_threat_level_is_valid_value(self, analyzer, full_profile):
        report = analyzer.analyze(full_profile)
        valid_levels = ("critical", "high", "moderate", "low", "unknown")
        assert report.overall_threat_level in valid_levels


# ---------------------------------------------------------------------------
# Regression Tests — Demo fixtures
# ---------------------------------------------------------------------------

class TestDemoFixturesRegression:
    """Testes de regressão com os fixtures de demonstração."""

    def test_all_demo_opponents_can_be_analyzed(self, analyzer):
        from src.opponent_prep.opponent_fixtures import build_demo_opponents
        opponents = build_demo_opponents()
        assert len(opponents) == 3
        for opp in opponents:
            report = analyzer.analyze(opp["profile"], opp["name"])
            assert isinstance(report, OpponentAnalysisReport)
            assert report.opponent_id == opp["profile"].opponent_id

    def test_demo_opp_001_high_pressing(self, analyzer):
        from src.opponent_prep.opponent_fixtures import get_demo_opponent_by_id
        opp = get_demo_opponent_by_id("demo-opp-001")
        assert opp is not None
        report = analyzer.analyze(opp["profile"], opp["name"])
        assert report.pressing_analysis.intensity == "high"

    def test_demo_opp_002_low_pressing(self, analyzer):
        from src.opponent_prep.opponent_fixtures import get_demo_opponent_by_id
        opp = get_demo_opponent_by_id("demo-opp-002")
        assert opp is not None
        report = analyzer.analyze(opp["profile"], opp["name"])
        assert report.pressing_analysis.intensity == "low"

    def test_demo_opp_003_medium_pressing(self, analyzer):
        from src.opponent_prep.opponent_fixtures import get_demo_opponent_by_id
        opp = get_demo_opponent_by_id("demo-opp-003")
        assert opp is not None
        report = analyzer.analyze(opp["profile"], opp["name"])
        assert report.pressing_analysis.intensity == "medium"

    def test_all_demo_reports_have_zone_vulnerabilities(self, analyzer):
        from src.opponent_prep.opponent_fixtures import build_demo_opponents
        for opp in build_demo_opponents():
            report = analyzer.analyze(opp["profile"], opp["name"])
            assert len(report.zone_vulnerabilities) > 0, \
                f"{opp['name']} should have zone vulnerabilities"

    def test_all_demo_reports_have_tactical_alerts(self, analyzer):
        from src.opponent_prep.opponent_fixtures import build_demo_opponents
        for opp in build_demo_opponents():
            report = analyzer.analyze(opp["profile"], opp["name"])
            assert len(report.tactical_alerts) > 0, \
                f"{opp['name']} should have tactical alerts"
