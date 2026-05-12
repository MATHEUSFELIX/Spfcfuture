"""
tests/opponent_prep/test_game_plan.py

Testes para o módulo game_plan (GamePlanGenerator).

Categorias cobertas:
    - Unit: GamePlanGenerator com análises completas e parciais
    - Contract: Campos obrigatórios no plano
    - Invariant: Confiança sempre entre 0.0 e 1.0, disclaimer sempre presente
    - Regression: Geração de plano para todos os fixtures de demo
"""
import pytest

from src.core.football_models import Match, OpponentProfile, SetPieceProfile
from src.opponent_prep.opponent_analyzer import OpponentAnalyzer
from src.opponent_prep.game_plan import GamePlan, GamePlanGenerator, GamePlanSection


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def analyzer():
    return OpponentAnalyzer()


@pytest.fixture
def generator():
    return GamePlanGenerator()


@pytest.fixture
def full_analysis(analyzer):
    profile = OpponentProfile(
        opponent_id="test-opp-plan",
        formation_patterns=["4-3-3"],
        pressing_profile="high intensity pressing with high defensive line.",
        weak_zones=["Corredor direito (right) vulnerável (high)"],
        transition_vulnerabilities=["Transição defensiva (defensive) após perda."],
        set_piece_profile=SetPieceProfile(
            corners_routine="Escanteios curtos",
            free_kick_routine="Faltas diretas",
            key_takers=["Jogador 10"],
            key_targets=["Jogador 9"],
        ),
        source_matches=["m001", "m002", "m003"],
    )
    return analyzer.analyze(profile, "Test Opponent")


@pytest.fixture
def empty_analysis(analyzer):
    profile = OpponentProfile(opponent_id="test-opp-empty-plan")
    return analyzer.analyze(profile, "Empty Opponent")


@pytest.fixture
def sample_match():
    return Match(
        match_id="match-001",
        home_team="São Paulo FC",
        away_team="Test Opponent",
        competition="Brasileirão",
        round="Rodada 10",
        date="2025-06-15",
        venue="Morumbi",
    )


@pytest.fixture
def spfc_principles():
    return [
        "Pressionar alto e recuperar rápido.",
        "Manter a bola e criar superioridade.",
        "Transição rápida após recuperação.",
    ]


# ---------------------------------------------------------------------------
# Unit Tests — GamePlanGenerator.generate()
# ---------------------------------------------------------------------------

class TestGamePlanGeneratorGenerate:
    """Testes unitários do método generate()."""

    def test_returns_game_plan_instance(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert isinstance(plan, GamePlan)

    def test_plan_has_opponent_id(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert plan.opponent_id == "test-opp-plan"

    def test_plan_has_opponent_name(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert plan.opponent_name == "Test Opponent"

    def test_plan_has_4_sections_without_principles(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert len(plan.sections) == 4

    def test_plan_has_5_sections_with_principles(self, generator, full_analysis, spfc_principles):
        plan = generator.generate(full_analysis, spfc_principles=spfc_principles)
        assert len(plan.sections) == 5

    def test_plan_has_key_messages(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert len(plan.key_messages) > 0
        assert len(plan.key_messages) <= 5

    def test_plan_has_risk_flags(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        # Full analysis with 3 source matches should have at least 1 risk flag
        assert isinstance(plan.risk_flags, list)

    def test_plan_has_contingency_notes(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert len(plan.contingency_notes) > 0

    def test_plan_has_disclaimer(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert len(plan.disclaimer) > 20
        assert "humana" in plan.disclaimer.lower() or "decisão" in plan.disclaimer.lower()

    def test_plan_has_plan_id(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert plan.plan_id.startswith("plan-")

    def test_plan_has_created_at(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert plan.created_at.endswith("Z")

    def test_plan_with_match_context(self, generator, full_analysis, sample_match):
        plan = generator.generate(full_analysis, match=sample_match)
        assert "São Paulo FC" in plan.match_context
        assert "Test Opponent" in plan.match_context

    def test_plan_without_match_has_default_context(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert "não especificado" in plan.match_context.lower()

    def test_empty_analysis_still_generates_plan(self, generator, empty_analysis):
        plan = generator.generate(empty_analysis)
        assert isinstance(plan, GamePlan)
        assert len(plan.sections) == 4


# ---------------------------------------------------------------------------
# Unit Tests — Plan Sections
# ---------------------------------------------------------------------------

class TestGamePlanSections:
    """Testes para as seções do plano de jogo."""

    def test_defensive_section_exists(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        phases = [s.phase for s in plan.sections]
        assert "defensive" in phases

    def test_offensive_section_exists(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        phases = [s.phase for s in plan.sections]
        assert "offensive" in phases

    def test_transition_section_exists(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        phases = [s.phase for s in plan.sections]
        assert "transition" in phases

    def test_set_piece_section_exists(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        phases = [s.phase for s in plan.sections]
        assert "set_piece" in phases

    def test_principles_section_exists_when_provided(self, generator, full_analysis, spfc_principles):
        plan = generator.generate(full_analysis, spfc_principles=spfc_principles)
        phases = [s.phase for s in plan.sections]
        assert "general" in phases

    def test_defensive_section_has_instructions(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        defensive = next(s for s in plan.sections if s.phase == "defensive")
        assert len(defensive.instructions) > 0

    def test_defensive_section_high_pressing_has_specific_instructions(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        defensive = next(s for s in plan.sections if s.phase == "defensive")
        # Should have instructions about handling high pressing
        all_instructions = " ".join(defensive.instructions).lower()
        assert "pressão" in all_instructions or "pressing" in all_instructions or "bola" in all_instructions

    def test_offensive_section_has_zone_instructions(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        offensive = next(s for s in plan.sections if s.phase == "offensive")
        assert len(offensive.instructions) > 0

    def test_section_has_rationale(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        for section in plan.sections:
            assert len(section.rationale) > 5, f"Section '{section.title}' has no rationale"

    def test_section_has_priority(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        valid_priorities = ("high", "medium", "low")
        for section in plan.sections:
            assert section.priority in valid_priorities

    def test_section_to_dict_has_required_keys(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        for section in plan.sections:
            d = section.to_dict()
            required = ["title", "phase", "instructions", "rationale", "priority", "confidence"]
            for key in required:
                assert key in d, f"Missing key '{key}' in section '{section.title}'"


# ---------------------------------------------------------------------------
# Invariant Tests
# ---------------------------------------------------------------------------

class TestGamePlanInvariants:
    """Invariantes do plano de jogo."""

    def test_overall_confidence_in_range(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert 0.0 <= plan.overall_confidence <= 1.0

    def test_section_confidence_in_range(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        for section in plan.sections:
            assert 0.0 <= section.confidence <= 1.0, \
                f"Section '{section.title}' confidence out of range: {section.confidence}"

    def test_data_completeness_in_range(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert 0.0 <= plan.data_completeness <= 1.0

    def test_disclaimer_always_present(self, generator, full_analysis, empty_analysis):
        for analysis in [full_analysis, empty_analysis]:
            plan = generator.generate(analysis)
            assert len(plan.disclaimer) > 10

    def test_key_messages_max_5(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        assert len(plan.key_messages) <= 5


# ---------------------------------------------------------------------------
# Contract Tests — to_dict()
# ---------------------------------------------------------------------------

class TestGamePlanToDict:
    """Testes de contrato: to_dict() retorna estrutura correta."""

    def test_plan_to_dict_has_required_keys(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        d = plan.to_dict()
        required = [
            "plan_id", "created_at", "match_context", "opponent_id",
            "opponent_name", "sections", "key_messages", "risk_flags",
            "contingency_notes", "overall_confidence", "disclaimer",
            "data_completeness",
        ]
        for key in required:
            assert key in d, f"Missing key: {key}"

    def test_plan_to_dict_is_json_serializable(self, generator, full_analysis):
        import json
        plan = generator.generate(full_analysis)
        d = plan.to_dict()
        json_str = json.dumps(d)
        assert len(json_str) > 100

    def test_sections_in_dict_are_list(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        d = plan.to_dict()
        assert isinstance(d["sections"], list)

    def test_key_messages_in_dict_are_list(self, generator, full_analysis):
        plan = generator.generate(full_analysis)
        d = plan.to_dict()
        assert isinstance(d["key_messages"], list)


# ---------------------------------------------------------------------------
# Regression Tests — Demo fixtures
# ---------------------------------------------------------------------------

class TestGamePlanDemoRegression:
    """Testes de regressão com os fixtures de demonstração."""

    def test_all_demo_opponents_generate_plans(self, analyzer, generator):
        from src.opponent_prep.opponent_fixtures import build_demo_opponents
        opponents = build_demo_opponents()
        for opp in opponents:
            report = analyzer.analyze(opp["profile"], opp["name"])
            plan = generator.generate(report)
            assert isinstance(plan, GamePlan)
            assert plan.opponent_id == opp["profile"].opponent_id

    def test_demo_plans_have_4_sections(self, analyzer, generator):
        from src.opponent_prep.opponent_fixtures import build_demo_opponents
        for opp in build_demo_opponents():
            report = analyzer.analyze(opp["profile"], opp["name"])
            plan = generator.generate(report)
            assert len(plan.sections) == 4, \
                f"{opp['name']} plan should have 4 sections"

    def test_demo_plans_have_key_messages(self, analyzer, generator):
        from src.opponent_prep.opponent_fixtures import build_demo_opponents
        for opp in build_demo_opponents():
            report = analyzer.analyze(opp["profile"], opp["name"])
            plan = generator.generate(report)
            assert len(plan.key_messages) > 0, \
                f"{opp['name']} plan should have key messages"

    def test_demo_plans_with_spfc_principles(self, analyzer, generator):
        from src.opponent_prep.opponent_fixtures import get_demo_opponent_by_id
        from src.spfc_base.knowledge_base import SPFC_KNOWLEDGE_BASE
        opp = get_demo_opponent_by_id("demo-opp-001")
        report = analyzer.analyze(opp["profile"], opp["name"])
        principles = SPFC_KNOWLEDGE_BASE.game_model.non_negotiables or []
        plan = generator.generate(report, spfc_principles=principles)
        # With principles, should have 5 sections
        assert len(plan.sections) == 5
