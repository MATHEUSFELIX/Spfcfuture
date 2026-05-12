"""
tests/spfc_base/test_knowledge_base.py — Testes da Base de Conhecimento SPFC.

Categoria: Domain Model Tests
Gate: Gate 1 — Unit Tests
"""
import pytest

from src.spfc_base.knowledge_base import (
    ClubIdentity,
    GameModel,
    KnowledgeBase,
    Phase,
    SPFC_KNOWLEDGE_BASE,
    TacticalPrinciple,
    build_spfc_reference_knowledge_base,
)


# ---------------------------------------------------------------------------
# ClubIdentity
# ---------------------------------------------------------------------------

class TestClubIdentity:
    def test_default_club_name(self):
        identity = ClubIdentity()
        assert identity.club_name == "São Paulo Futebol Clube"

    def test_default_founded_year(self):
        identity = ClubIdentity()
        assert identity.founded == 1930

    def test_titles_summary_not_empty(self):
        identity = ClubIdentity()
        assert len(identity.titles_summary) > 0

    def test_tactical_heritage_not_empty(self):
        identity = ClubIdentity()
        assert len(identity.tactical_heritage) > 0

    def test_current_season_default(self):
        identity = ClubIdentity()
        assert identity.current_season == "a definir"

    def test_to_dict_has_required_keys(self):
        identity = ClubIdentity()
        d = identity.to_dict()
        assert "club_name" in d
        assert "founded" in d
        assert "titles_summary" in d
        assert "tactical_heritage" in d
        assert "current_season" in d
        assert "current_competition" in d

    def test_to_dict_values_match(self):
        identity = ClubIdentity(club_name="Test Club", founded=2000)
        d = identity.to_dict()
        assert d["club_name"] == "Test Club"
        assert d["founded"] == 2000


# ---------------------------------------------------------------------------
# Phase
# ---------------------------------------------------------------------------

class TestPhase:
    def test_phase_creation(self):
        phase = Phase(
            name="Organização Defensiva",
            principles=["Bloco médio-baixo"],
            tasks=["Fechar espaços centrais"],
            key_metrics=["PPDA"],
        )
        assert phase.name == "Organização Defensiva"
        assert len(phase.principles) == 1
        assert len(phase.tasks) == 1
        assert len(phase.key_metrics) == 1

    def test_phase_to_dict(self):
        phase = Phase(name="Test Phase", principles=["p1"], tasks=["t1"])
        d = phase.to_dict()
        assert d["name"] == "Test Phase"
        assert d["principles"] == ["p1"]
        assert d["tasks"] == ["t1"]
        assert "key_metrics" in d

    def test_phase_empty_defaults(self):
        phase = Phase(name="Empty")
        assert phase.principles == []
        assert phase.tasks == []
        assert phase.key_metrics == []


# ---------------------------------------------------------------------------
# TacticalPrinciple
# ---------------------------------------------------------------------------

class TestTacticalPrinciple:
    def test_principle_creation(self):
        p = TacticalPrinciple(
            id="tp-001",
            category="posse",
            description="Construção desde o goleiro.",
            rationale="Manter posse.",
            observable_indicators=["Goleiro distribui curto."],
        )
        assert p.id == "tp-001"
        assert p.category == "posse"

    def test_principle_to_dict(self):
        p = TacticalPrinciple(id="tp-test", category="pressão", description="Test")
        d = p.to_dict()
        assert d["id"] == "tp-test"
        assert d["category"] == "pressão"
        assert "observable_indicators" in d

    def test_principle_default_id(self):
        p = TacticalPrinciple()
        assert p.id == "unknown"


# ---------------------------------------------------------------------------
# GameModel
# ---------------------------------------------------------------------------

class TestGameModel:
    def test_default_formation(self):
        gm = GameModel()
        assert gm.preferred_formation == "4-3-3"

    def test_to_dict_has_phases(self):
        gm = GameModel(phases=[Phase(name="P1"), Phase(name="P2")])
        d = gm.to_dict()
        assert len(d["phases"]) == 2

    def test_to_dict_has_non_negotiables(self):
        gm = GameModel(non_negotiables=["Princípio 1", "Princípio 2"])
        d = gm.to_dict()
        assert len(d["non_negotiables"]) == 2


# ---------------------------------------------------------------------------
# KnowledgeBase
# ---------------------------------------------------------------------------

class TestKnowledgeBase:
    def test_get_principle_found(self):
        kb = build_spfc_reference_knowledge_base()
        p = kb.get_principle("tp-001")
        assert p is not None
        assert p.id == "tp-001"

    def test_get_principle_not_found(self):
        kb = build_spfc_reference_knowledge_base()
        p = kb.get_principle("tp-999")
        assert p is None

    def test_get_principles_by_category(self):
        kb = build_spfc_reference_knowledge_base()
        posse = kb.get_principles_by_category("posse")
        assert len(posse) >= 1
        assert all(p.category == "posse" for p in posse)

    def test_get_principles_by_unknown_category(self):
        kb = build_spfc_reference_knowledge_base()
        result = kb.get_principles_by_category("categoria_inexistente")
        assert result == []

    def test_to_dict_structure(self):
        kb = build_spfc_reference_knowledge_base()
        d = kb.to_dict()
        assert "identity" in d
        assert "game_model" in d
        assert "tactical_principles" in d

    def test_to_dict_principles_list(self):
        kb = build_spfc_reference_knowledge_base()
        d = kb.to_dict()
        assert isinstance(d["tactical_principles"], list)
        assert len(d["tactical_principles"]) > 0


# ---------------------------------------------------------------------------
# build_spfc_reference_knowledge_base
# ---------------------------------------------------------------------------

class TestBuildSpfcReferenceKnowledgeBase:
    def test_returns_knowledge_base_instance(self):
        kb = build_spfc_reference_knowledge_base()
        assert isinstance(kb, KnowledgeBase)

    def test_has_4_phases(self):
        kb = build_spfc_reference_knowledge_base()
        assert len(kb.game_model.phases) == 4

    def test_has_12_principles(self):
        kb = build_spfc_reference_knowledge_base()
        assert len(kb.tactical_principles) == 12

    def test_has_4_non_negotiables(self):
        kb = build_spfc_reference_knowledge_base()
        assert len(kb.game_model.non_negotiables) == 4

    def test_phase_names(self):
        kb = build_spfc_reference_knowledge_base()
        names = [p.name for p in kb.game_model.phases]
        assert "Organização Defensiva" in names
        assert "Transição Defensiva" in names
        assert "Organização Ofensiva" in names
        assert "Transição Ofensiva" in names

    def test_all_principles_have_ids(self):
        kb = build_spfc_reference_knowledge_base()
        for p in kb.tactical_principles:
            assert p.id != "unknown"
            assert p.id.startswith("tp-")

    def test_all_principles_have_categories(self):
        kb = build_spfc_reference_knowledge_base()
        for p in kb.tactical_principles:
            assert p.category != "unknown"

    def test_all_principles_have_descriptions(self):
        kb = build_spfc_reference_knowledge_base()
        for p in kb.tactical_principles:
            assert len(p.description) > 0

    def test_all_principles_have_rationale(self):
        kb = build_spfc_reference_knowledge_base()
        for p in kb.tactical_principles:
            assert len(p.rationale) > 0

    def test_bola_parada_principles_exist(self):
        kb = build_spfc_reference_knowledge_base()
        bp = kb.get_principles_by_category("bola_parada")
        assert len(bp) >= 2

    def test_transicao_principles_exist(self):
        kb = build_spfc_reference_knowledge_base()
        trans = kb.get_principles_by_category("transição")
        assert len(trans) >= 2

    def test_preferred_formation_is_433(self):
        kb = build_spfc_reference_knowledge_base()
        assert kb.game_model.preferred_formation == "4-3-3"

    def test_style_keywords_not_empty(self):
        kb = build_spfc_reference_knowledge_base()
        assert len(kb.game_model.style_keywords) > 0

    def test_singleton_is_same_instance(self):
        """SPFC_KNOWLEDGE_BASE singleton deve ser consistente."""
        kb1 = SPFC_KNOWLEDGE_BASE
        kb2 = SPFC_KNOWLEDGE_BASE
        assert kb1 is kb2

    def test_singleton_has_correct_identity(self):
        assert SPFC_KNOWLEDGE_BASE.identity.club_name == "São Paulo Futebol Clube"

    def test_each_phase_has_principles(self):
        kb = build_spfc_reference_knowledge_base()
        for phase in kb.game_model.phases:
            assert len(phase.principles) > 0, f"Phase '{phase.name}' has no principles"

    def test_each_phase_has_tasks(self):
        kb = build_spfc_reference_knowledge_base()
        for phase in kb.game_model.phases:
            assert len(phase.tasks) > 0, f"Phase '{phase.name}' has no tasks"
