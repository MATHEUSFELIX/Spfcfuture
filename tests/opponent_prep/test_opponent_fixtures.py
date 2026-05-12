"""
tests/opponent_prep/test_opponent_fixtures.py

Testes para o módulo opponent_fixtures.

Categorias cobertas:
    - Unit: build_demo_opponents() e get_demo_opponent_by_id()
    - Contract: Estrutura dos fixtures
    - Boundary: IDs válidos e inválidos
    - Invariant: Dados marcados como demo
"""
import pytest

from src.opponent_prep.opponent_fixtures import (
    build_demo_opponents,
    get_demo_opponent_by_id,
)
from src.core.football_models import OpponentProfile


# ---------------------------------------------------------------------------
# Unit Tests — build_demo_opponents()
# ---------------------------------------------------------------------------

class TestBuildDemoOpponents:
    """Testes para a função build_demo_opponents()."""

    def test_returns_list(self):
        result = build_demo_opponents()
        assert isinstance(result, list)

    def test_returns_3_opponents(self):
        result = build_demo_opponents()
        assert len(result) == 3

    def test_each_item_has_profile_key(self):
        for opp in build_demo_opponents():
            assert "profile" in opp, f"Missing 'profile' key in opponent: {opp}"

    def test_each_item_has_name_key(self):
        for opp in build_demo_opponents():
            assert "name" in opp, f"Missing 'name' key in opponent: {opp}"

    def test_each_item_has_description_key(self):
        for opp in build_demo_opponents():
            assert "description" in opp, f"Missing 'description' key in opponent: {opp}"

    def test_each_profile_is_opponent_profile_instance(self):
        for opp in build_demo_opponents():
            assert isinstance(opp["profile"], OpponentProfile), \
                f"profile should be OpponentProfile, got {type(opp['profile'])}"

    def test_each_profile_has_opponent_id(self):
        for opp in build_demo_opponents():
            assert opp["profile"].opponent_id, "OpponentProfile must have opponent_id"

    def test_ids_are_unique(self):
        opponents = build_demo_opponents()
        ids = [opp["profile"].opponent_id for opp in opponents]
        assert len(ids) == len(set(ids)), "Opponent IDs must be unique"

    def test_names_are_unique(self):
        opponents = build_demo_opponents()
        names = [opp["name"] for opp in opponents]
        assert len(names) == len(set(names)), "Opponent names must be unique"

    def test_demo_ids_start_with_demo(self):
        for opp in build_demo_opponents():
            assert opp["profile"].opponent_id.startswith("demo-"), \
                f"Demo opponent ID should start with 'demo-': {opp['profile'].opponent_id}"

    def test_demo_names_contain_demo_marker(self):
        for opp in build_demo_opponents():
            assert "[Demo]" in opp["name"], \
                f"Demo opponent name should contain '[Demo]': {opp['name']}"

    def test_profiles_have_formation_patterns(self):
        for opp in build_demo_opponents():
            assert opp["profile"].formation_patterns, \
                f"{opp['name']} should have formation_patterns"

    def test_profiles_have_pressing_profile(self):
        for opp in build_demo_opponents():
            assert opp["profile"].pressing_profile, \
                f"{opp['name']} should have pressing_profile"

    def test_profiles_have_weak_zones(self):
        for opp in build_demo_opponents():
            assert opp["profile"].weak_zones, \
                f"{opp['name']} should have weak_zones"

    def test_profiles_have_source_matches(self):
        for opp in build_demo_opponents():
            assert opp["profile"].source_matches, \
                f"{opp['name']} should have source_matches"

    def test_profiles_have_set_piece_profile(self):
        for opp in build_demo_opponents():
            assert opp["profile"].set_piece_profile is not None, \
                f"{opp['name']} should have set_piece_profile"


# ---------------------------------------------------------------------------
# Unit Tests — get_demo_opponent_by_id()
# ---------------------------------------------------------------------------

class TestGetDemoOpponentById:
    """Testes para a função get_demo_opponent_by_id()."""

    def test_returns_opp_001(self):
        opp = get_demo_opponent_by_id("demo-opp-001")
        assert opp is not None

    def test_returns_opp_002(self):
        opp = get_demo_opponent_by_id("demo-opp-002")
        assert opp is not None

    def test_returns_opp_003(self):
        opp = get_demo_opponent_by_id("demo-opp-003")
        assert opp is not None

    def test_returns_none_for_invalid_id(self):
        opp = get_demo_opponent_by_id("nonexistent-id")
        assert opp is None

    def test_returns_none_for_empty_string(self):
        opp = get_demo_opponent_by_id("")
        assert opp is None

    def test_correct_profile_id_for_001(self):
        opp = get_demo_opponent_by_id("demo-opp-001")
        assert opp["profile"].opponent_id == "demo-opp-001"

    def test_correct_profile_id_for_002(self):
        opp = get_demo_opponent_by_id("demo-opp-002")
        assert opp["profile"].opponent_id == "demo-opp-002"

    def test_correct_profile_id_for_003(self):
        opp = get_demo_opponent_by_id("demo-opp-003")
        assert opp["profile"].opponent_id == "demo-opp-003"

    def test_returned_profile_is_opponent_profile(self):
        opp = get_demo_opponent_by_id("demo-opp-001")
        assert isinstance(opp["profile"], OpponentProfile)

    def test_case_sensitive_id_lookup(self):
        # IDs are lowercase, uppercase should not match
        opp = get_demo_opponent_by_id("DEMO-OPP-001")
        assert opp is None


# ---------------------------------------------------------------------------
# Invariant Tests — Demo data integrity
# ---------------------------------------------------------------------------

class TestDemoDataIntegrity:
    """Testes de integridade dos dados de demonstração."""

    def test_all_descriptions_are_non_empty(self):
        for opp in build_demo_opponents():
            assert len(opp["description"]) > 10, \
                f"{opp['name']} description is too short"

    def test_all_profiles_have_last_updated(self):
        for opp in build_demo_opponents():
            assert opp["profile"].last_updated, \
                f"{opp['name']} should have last_updated"

    def test_pressing_profiles_cover_all_intensities(self):
        """Os 3 fixtures devem cobrir pressing alto, médio e baixo."""
        from src.opponent_prep.opponent_analyzer import OpponentAnalyzer
        analyzer = OpponentAnalyzer()
        intensities = set()
        for opp in build_demo_opponents():
            report = analyzer.analyze(opp["profile"], opp["name"])
            intensities.add(report.pressing_analysis.intensity)
        assert "high" in intensities, "Should have at least one high pressing opponent"
        assert "low" in intensities, "Should have at least one low pressing opponent"

    def test_build_is_deterministic(self):
        """build_demo_opponents() deve retornar os mesmos dados em chamadas repetidas."""
        result1 = build_demo_opponents()
        result2 = build_demo_opponents()
        for opp1, opp2 in zip(result1, result2):
            assert opp1["profile"].opponent_id == opp2["profile"].opponent_id
            assert opp1["name"] == opp2["name"]
