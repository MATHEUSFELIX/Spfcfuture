"""
tests/squad_intelligence/test_squad_fixtures.py — Testes das Fixtures de Elenco.

Categoria: Domain Model Tests
Gate: Gate 1 — Unit Tests
"""
import pytest

from src.core.football_models import AvailabilityStatus
from src.squad_intelligence.squad_fixtures import build_demo_squad


class TestBuildDemoSquad:
    @pytest.fixture
    def squad(self):
        return build_demo_squad()

    def test_returns_non_empty_list(self, squad):
        assert len(squad) > 0

    def test_all_players_have_ids(self, squad):
        for p in squad:
            assert len(p.player_id) > 0
            assert p.player_id != "unknown"

    def test_all_players_have_names(self, squad):
        for p in squad:
            assert len(p.name) > 0

    def test_all_players_marked_as_fixture(self, squad):
        """Todos os jogadores de demo devem ter '[Demo]' no nome."""
        for p in squad:
            assert "[Demo]" in p.name, (
                f"Player '{p.name}' não está marcado como fixture"
            )

    def test_all_players_have_positions(self, squad):
        for p in squad:
            assert len(p.positions) > 0, (
                f"Player '{p.name}' has no positions"
            )

    def test_has_goalkeeper(self, squad):
        gks = [p for p in squad if "GK" in p.positions]
        assert len(gks) >= 2

    def test_has_defenders(self, squad):
        defenders = [p for p in squad if any(pos in ["CB", "RB", "LB"] for pos in p.positions)]
        assert len(defenders) >= 4

    def test_has_midfielders(self, squad):
        mids = [p for p in squad if any(pos in ["DM", "CM", "AM"] for pos in p.positions)]
        assert len(mids) >= 3

    def test_has_forwards(self, squad):
        forwards = [p for p in squad if any(pos in ["RW", "LW", "ST", "CF"] for pos in p.positions)]
        assert len(forwards) >= 4

    def test_has_some_unavailable_players(self, squad):
        """Deve haver pelo menos um jogador indisponível para demonstrar gaps."""
        unavailable = [
            p for p in squad
            if p.availability_status in (AvailabilityStatus.INJURED, AvailabilityStatus.SUSPENDED)
        ]
        assert len(unavailable) >= 1

    def test_all_players_have_notes(self, squad):
        """Todos os jogadores de demo devem ter nota explicando que são fictícios."""
        for p in squad:
            assert "fictício" in p.notes.lower() or "fixture" in p.notes.lower(), (
                f"Player '{p.name}' missing fixture disclaimer in notes"
            )

    def test_unique_player_ids(self, squad):
        ids = [p.player_id for p in squad]
        assert len(ids) == len(set(ids)), "Duplicate player IDs found"

    def test_ages_are_realistic(self, squad):
        """Idades devem estar em faixa realista para futebolistas profissionais."""
        for p in squad:
            if p.age is not None:
                assert 16 <= p.age <= 45, (
                    f"Player '{p.name}' has unrealistic age: {p.age}"
                )

    def test_squad_covers_433_positions(self, squad):
        """Elenco deve cobrir as posições básicas de um 4-3-3."""
        all_positions = set()
        for p in squad:
            all_positions.update(p.positions)
        required = {"GK", "CB", "RB", "LB", "DM", "CM", "RW", "LW", "ST"}
        missing = required - all_positions
        assert len(missing) == 0, f"Missing positions for 4-3-3: {missing}"
