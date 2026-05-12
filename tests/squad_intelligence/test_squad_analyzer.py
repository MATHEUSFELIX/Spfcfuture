"""
tests/squad_intelligence/test_squad_analyzer.py — Testes do Squad Analyzer.

Categoria: Domain Model Tests + Analytics Tests
Gate: Gate 1 — Unit Tests + Gate 2 — Integration Tests
"""
import pytest

from src.core.football_models import AvailabilityStatus, Foot, Player
from src.squad_intelligence.squad_analyzer import (
    AgeCurveAnalysis,
    GapAnalysis,
    RoleDefinition,
    SPFC_REFERENCE_ROLES,
    SquadAnalyzer,
    SquadAnalysisReport,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_player(
    player_id: str = "p1",
    name: str = "Test Player",
    positions: list = None,
    roles: list = None,
    age: int = 25,
    status: AvailabilityStatus = AvailabilityStatus.AVAILABLE,
) -> Player:
    return Player(
        player_id=player_id,
        name=name,
        age=age,
        preferred_foot=Foot.RIGHT,
        positions=positions or ["CB"],
        roles=roles or [],
        availability_status=status,
    )


@pytest.fixture
def analyzer():
    return SquadAnalyzer()


@pytest.fixture
def minimal_squad():
    """Elenco mínimo com 1 jogador por posição."""
    return [
        make_player("gk1", "Goleiro", ["GK"], ["gk"]),
        make_player("cb1", "Zagueiro", ["CB"], ["ball_playing_cb"]),
        make_player("rb1", "Lateral D", ["RB"], ["attacking_rb"]),
        make_player("lb1", "Lateral E", ["LB"], ["attacking_lb"]),
        make_player("dm1", "Volante", ["DM"], ["defensive_mid"]),
        make_player("cm1", "Meia", ["CM"], ["box_to_box_mid"]),
        make_player("rw1", "Extremo D", ["RW"], ["winger_right"]),
        make_player("lw1", "Extremo E", ["LW"], ["winger_left"]),
        make_player("st1", "Atacante", ["ST"], ["striker"]),
    ]


@pytest.fixture
def full_squad():
    """Elenco completo com cobertura adequada para todos os papéis."""
    players = []
    for i in range(2):
        players.append(make_player(f"gk{i}", f"Goleiro {i}", ["GK"], ["gk"]))
        players.append(make_player(f"cb{i}", f"Zagueiro {i}", ["CB"], ["ball_playing_cb"]))
        players.append(make_player(f"rb{i}", f"Lateral D {i}", ["RB"], ["attacking_rb"]))
        players.append(make_player(f"lb{i}", f"Lateral E {i}", ["LB"], ["attacking_lb"]))
        players.append(make_player(f"dm{i}", f"Volante {i}", ["DM"], ["defensive_mid"]))
        players.append(make_player(f"cm{i}", f"Meia {i}", ["CM"], ["box_to_box_mid"]))
        players.append(make_player(f"rw{i}", f"Extremo D {i}", ["RW"], ["winger_right"]))
        players.append(make_player(f"lw{i}", f"Extremo E {i}", ["LW"], ["winger_left"]))
        players.append(make_player(f"st{i}", f"Atacante {i}", ["ST"], ["striker"]))
    # Meia criativo extra
    players.append(make_player("cm_creative", "Meia Criativo", ["CM", "AM"], ["creative_mid"]))
    # Zagueiro marcador extra
    players.append(make_player("cb_stopper", "Zagueiro Marcador", ["CB"], ["stopper_cb"]))
    return players


# ---------------------------------------------------------------------------
# RoleDefinition
# ---------------------------------------------------------------------------

class TestRoleDefinition:
    def test_to_dict_has_required_keys(self):
        role = RoleDefinition(
            role_id="gk",
            name="Goleiro",
            positions=["GK"],
            minimum_squad_count=2,
        )
        d = role.to_dict()
        assert "role_id" in d
        assert "name" in d
        assert "positions" in d
        assert "minimum_squad_count" in d

    def test_spfc_reference_roles_not_empty(self):
        assert len(SPFC_REFERENCE_ROLES) > 0

    def test_all_reference_roles_have_ids(self):
        for role in SPFC_REFERENCE_ROLES:
            assert role.role_id != "unknown"

    def test_all_reference_roles_have_positions(self):
        for role in SPFC_REFERENCE_ROLES:
            assert len(role.positions) > 0

    def test_all_reference_roles_have_minimum(self):
        for role in SPFC_REFERENCE_ROLES:
            assert role.minimum_squad_count >= 1


# ---------------------------------------------------------------------------
# SquadAnalyzer — Basic
# ---------------------------------------------------------------------------

class TestSquadAnalyzerBasic:
    def test_analyze_empty_squad(self, analyzer):
        report = analyzer.analyze([], team_id="test", season="2025")
        assert report.total_players == 0
        assert report.available_players == 0
        assert report.unavailable_players == 0

    def test_analyze_returns_report_instance(self, analyzer, minimal_squad):
        report = analyzer.analyze(minimal_squad)
        assert isinstance(report, SquadAnalysisReport)

    def test_total_players_count(self, analyzer, minimal_squad):
        report = analyzer.analyze(minimal_squad)
        assert report.total_players == len(minimal_squad)

    def test_all_available_squad(self, analyzer):
        players = [
            make_player("p1", status=AvailabilityStatus.AVAILABLE),
            make_player("p2", status=AvailabilityStatus.AVAILABLE),
        ]
        report = analyzer.analyze(players)
        assert report.available_players == 2
        assert report.unavailable_players == 0

    def test_injured_player_counted_as_unavailable(self, analyzer):
        players = [
            make_player("p1", status=AvailabilityStatus.AVAILABLE),
            make_player("p2", status=AvailabilityStatus.INJURED),
        ]
        report = analyzer.analyze(players)
        assert report.available_players == 1
        assert report.unavailable_players == 1

    def test_suspended_player_counted_as_unavailable(self, analyzer):
        players = [
            make_player("p1", status=AvailabilityStatus.AVAILABLE),
            make_player("p2", status=AvailabilityStatus.SUSPENDED),
        ]
        report = analyzer.analyze(players)
        assert report.unavailable_players == 1

    def test_doubtful_player_counted_as_available(self, analyzer):
        """Jogadores com dúvida são contados como disponíveis (conservador)."""
        players = [
            make_player("p1", status=AvailabilityStatus.DOUBTFUL),
        ]
        report = analyzer.analyze(players)
        assert report.available_players == 1
        assert report.unavailable_players == 0

    def test_team_id_and_season_preserved(self, analyzer):
        report = analyzer.analyze([], team_id="spfc", season="2025")
        assert report.team_id == "spfc"
        assert report.season == "2025"


# ---------------------------------------------------------------------------
# SquadAnalyzer — Depth Analysis
# ---------------------------------------------------------------------------

class TestSquadAnalyzerDepth:
    def test_depth_by_position_not_empty(self, analyzer, minimal_squad):
        report = analyzer.analyze(minimal_squad)
        assert len(report.depth_by_position) > 0

    def test_single_player_position_has_gap(self, analyzer):
        players = [make_player("gk1", positions=["GK"], roles=["gk"])]
        report = analyzer.analyze(players)
        gk_depth = next((d for d in report.depth_by_position if d.position == "GK"), None)
        assert gk_depth is not None
        assert gk_depth.has_gap is True

    def test_two_players_same_position_no_gap(self, analyzer):
        players = [
            make_player("gk1", positions=["GK"], roles=["gk"]),
            make_player("gk2", positions=["GK"], roles=["gk"]),
        ]
        report = analyzer.analyze(players)
        gk_depth = next((d for d in report.depth_by_position if d.position == "GK"), None)
        assert gk_depth is not None
        assert gk_depth.has_gap is False

    def test_injured_player_not_counted_in_depth(self, analyzer):
        players = [
            make_player("gk1", positions=["GK"], status=AvailabilityStatus.AVAILABLE),
            make_player("gk2", positions=["GK"], status=AvailabilityStatus.INJURED),
        ]
        report = analyzer.analyze(players)
        gk_depth = next((d for d in report.depth_by_position if d.position == "GK"), None)
        assert gk_depth is not None
        assert gk_depth.depth_count == 1  # apenas o disponível


# ---------------------------------------------------------------------------
# SquadAnalyzer — Gap Analysis
# ---------------------------------------------------------------------------

class TestSquadAnalyzerGaps:
    def test_gap_analysis_not_empty(self, analyzer, minimal_squad):
        report = analyzer.analyze(minimal_squad)
        assert len(report.gap_analysis) > 0

    def test_no_players_for_role_is_critical(self, analyzer):
        """Elenco vazio deve ter todos os papéis como críticos."""
        report = analyzer.analyze([])
        critical = [g for g in report.gap_analysis if g.gap_severity == "critical"]
        assert len(critical) > 0

    def test_full_squad_has_no_critical_gaps(self, analyzer, full_squad):
        report = analyzer.analyze(full_squad)
        critical = [g for g in report.gap_analysis if g.gap_severity == "critical"]
        assert len(critical) == 0

    def test_gap_severity_values_are_valid(self, analyzer, minimal_squad):
        report = analyzer.analyze(minimal_squad)
        valid_severities = {"critical", "moderate", "minor", "none"}
        for gap in report.gap_analysis:
            assert gap.gap_severity in valid_severities

    def test_gap_explanation_not_empty_for_gaps(self, analyzer):
        """Lacunas identificadas devem ter explicação."""
        report = analyzer.analyze([])
        for gap in report.gap_analysis:
            if gap.gap_severity != "none":
                assert len(gap.explanation) > 0

    def test_gap_suggested_action_for_critical(self, analyzer):
        """Lacunas críticas devem ter ação sugerida."""
        report = analyzer.analyze([])
        for gap in report.gap_analysis:
            if gap.gap_severity == "critical":
                assert len(gap.suggested_action) > 0

    def test_gap_to_dict_structure(self, analyzer):
        report = analyzer.analyze([])
        for gap in report.gap_analysis:
            d = gap.to_dict()
            assert "role_id" in d
            assert "role_name" in d
            assert "gap_severity" in d
            assert "explanation" in d


# ---------------------------------------------------------------------------
# SquadAnalyzer — Age Curve
# ---------------------------------------------------------------------------

class TestSquadAnalyzerAgeCurve:
    def test_age_curve_u23(self, analyzer):
        players = [make_player("p1", age=20), make_player("p2", age=22)]
        report = analyzer.analyze(players)
        assert report.age_curve.u23_count == 2

    def test_age_curve_prime(self, analyzer):
        players = [make_player("p1", age=25), make_player("p2", age=28)]
        report = analyzer.analyze(players)
        assert report.age_curve.prime_count == 2

    def test_age_curve_experienced(self, analyzer):
        players = [make_player("p1", age=31), make_player("p2", age=35)]
        report = analyzer.analyze(players)
        assert report.age_curve.experienced_count == 2

    def test_age_curve_unknown_age(self, analyzer):
        players = [make_player("p1", age=None)]
        report = analyzer.analyze(players)
        assert report.age_curve.unknown_age_count == 1

    def test_average_age_calculated(self, analyzer):
        players = [make_player("p1", age=20), make_player("p2", age=30)]
        report = analyzer.analyze(players)
        assert report.age_curve.average_age == 25.0

    def test_average_age_none_when_all_unknown(self, analyzer):
        players = [make_player("p1", age=None)]
        report = analyzer.analyze(players)
        assert report.age_curve.average_age is None

    def test_age_curve_to_dict(self, analyzer):
        players = [make_player("p1", age=25)]
        report = analyzer.analyze(players)
        d = report.age_curve.to_dict()
        assert "u23_count" in d
        assert "prime_count" in d
        assert "experienced_count" in d
        assert "average_age" in d


# ---------------------------------------------------------------------------
# SquadAnalyzer — Key Dependencies
# ---------------------------------------------------------------------------

class TestSquadAnalyzerDependencies:
    def test_single_player_per_role_is_dependency(self, analyzer):
        players = [make_player("gk1", positions=["GK"], roles=["gk"])]
        report = analyzer.analyze(players)
        # Deve identificar o goleiro como dependência
        assert len(report.key_dependencies) >= 1
        assert any("Goleiro" in dep for dep in report.key_dependencies)

    def test_two_players_per_role_no_dependency(self, analyzer):
        players = [
            make_player("gk1", positions=["GK"], roles=["gk"]),
            make_player("gk2", positions=["GK"], roles=["gk"]),
        ]
        # Com 2 goleiros, não deve ser dependência crítica
        report = analyzer.analyze(players)
        gk_deps = [d for d in report.key_dependencies if "Goleiro" in d]
        assert len(gk_deps) == 0


# ---------------------------------------------------------------------------
# SquadAnalyzer — Overall Assessment
# ---------------------------------------------------------------------------

class TestSquadAnalyzerAssessment:
    def test_empty_squad_has_assessment(self, analyzer):
        report = analyzer.analyze([])
        assert len(report.overall_assessment) > 0

    def test_critical_gaps_mentioned_in_assessment(self, analyzer):
        report = analyzer.analyze([])
        assert "crítica" in report.overall_assessment.lower()

    def test_full_squad_adequate_assessment(self, analyzer, full_squad):
        report = analyzer.analyze(full_squad)
        assert "adequada" in report.overall_assessment.lower()

    def test_data_completeness_zero_for_no_positions(self, analyzer):
        players = [Player(player_id="p1", name="Test", positions=[])]
        report = analyzer.analyze(players)
        assert report.data_completeness == 0.0

    def test_data_completeness_one_for_all_with_positions(self, analyzer):
        players = [make_player("p1", positions=["GK"])]
        report = analyzer.analyze(players)
        assert report.data_completeness == 1.0

    def test_report_to_dict_structure(self, analyzer, minimal_squad):
        report = analyzer.analyze(minimal_squad)
        d = report.to_dict()
        assert "team_id" in d
        assert "total_players" in d
        assert "available_players" in d
        assert "gap_analysis" in d
        assert "age_curve" in d
        assert "recommendations" in d
        assert "data_completeness" in d


# ---------------------------------------------------------------------------
# SquadAnalyzer — Custom Roles
# ---------------------------------------------------------------------------

class TestSquadAnalyzerCustomRoles:
    def test_custom_roles_used_instead_of_default(self, analyzer):
        custom_roles = [
            RoleDefinition(
                role_id="custom_gk",
                name="Custom Goleiro",
                positions=["GK"],
                minimum_squad_count=1,
            )
        ]
        players = [make_player("gk1", positions=["GK"])]
        report = analyzer.analyze(players, reference_roles=custom_roles)
        assert len(report.gap_analysis) == 1
        assert report.gap_analysis[0].role_id == "custom_gk"
