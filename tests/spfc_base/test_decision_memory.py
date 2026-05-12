"""
tests/spfc_base/test_decision_memory.py — Testes da Memória de Decisões.

Categoria: Domain Model Tests + Persistence Tests
Gate: Gate 1 — Unit Tests
"""
import json
import pytest
from pathlib import Path

from src.spfc_base.decision_memory import DecisionEntry, DecisionMemory


# ---------------------------------------------------------------------------
# DecisionEntry
# ---------------------------------------------------------------------------

class TestDecisionEntry:
    def test_default_entry_has_id(self):
        entry = DecisionEntry()
        assert len(entry.entry_id) > 0

    def test_default_entry_has_timestamp(self):
        entry = DecisionEntry()
        assert entry.created_at.endswith("Z")

    def test_to_dict_has_required_keys(self):
        entry = DecisionEntry(
            context="Jogo vs Flamengo",
            decision_taken="Mudar para 4-4-2",
        )
        d = entry.to_dict()
        assert "entry_id" in d
        assert "created_at" in d
        assert "context" in d
        assert "decision_taken" in d
        assert "alternatives_considered" in d
        assert "rationale" in d
        assert "outcome" in d
        assert "feedback" in d
        assert "tags" in d

    def test_from_dict_roundtrip(self):
        entry = DecisionEntry(
            context="Test context",
            decision_taken="Test decision",
            tags=["tag1", "tag2"],
            run_id="run-123",
        )
        d = entry.to_dict()
        restored = DecisionEntry.from_dict(d)
        assert restored.entry_id == entry.entry_id
        assert restored.context == entry.context
        assert restored.decision_taken == entry.decision_taken
        assert restored.tags == entry.tags
        assert restored.run_id == entry.run_id

    def test_from_dict_missing_fields_use_defaults(self):
        entry = DecisionEntry.from_dict({})
        assert len(entry.entry_id) > 0
        assert entry.context == ""
        assert entry.tags == []

    def test_outcome_default_is_none(self):
        entry = DecisionEntry()
        assert entry.outcome is None

    def test_feedback_default_is_none(self):
        entry = DecisionEntry()
        assert entry.feedback is None


# ---------------------------------------------------------------------------
# DecisionMemory
# ---------------------------------------------------------------------------

class TestDecisionMemory:
    @pytest.fixture
    def tmp_memory(self, tmp_path):
        """Cria uma instância de DecisionMemory com arquivo temporário."""
        memory_file = tmp_path / "test_memory.json"
        return DecisionMemory(memory_file=memory_file)

    def test_empty_memory_has_zero_count(self, tmp_memory):
        assert tmp_memory.count() == 0

    def test_add_entry_increments_count(self, tmp_memory):
        entry = DecisionEntry(context="Test", decision_taken="Decision A")
        tmp_memory.add(entry)
        assert tmp_memory.count() == 1

    def test_add_multiple_entries(self, tmp_memory):
        for i in range(5):
            tmp_memory.add(DecisionEntry(context=f"Context {i}"))
        assert tmp_memory.count() == 5

    def test_get_all_returns_most_recent_first(self, tmp_memory):
        e1 = DecisionEntry(context="First")
        e2 = DecisionEntry(context="Second")
        e3 = DecisionEntry(context="Third")
        tmp_memory.add(e1)
        tmp_memory.add(e2)
        tmp_memory.add(e3)
        all_entries = tmp_memory.get_all()
        assert all_entries[0].context == "Third"
        assert all_entries[-1].context == "First"

    def test_get_by_tag(self, tmp_memory):
        e1 = DecisionEntry(context="A", tags=["tático", "urgente"])
        e2 = DecisionEntry(context="B", tags=["tático"])
        e3 = DecisionEntry(context="C", tags=["elenco"])
        tmp_memory.add(e1)
        tmp_memory.add(e2)
        tmp_memory.add(e3)
        result = tmp_memory.get_by_tag("tático")
        assert len(result) == 2

    def test_get_by_tag_no_match(self, tmp_memory):
        tmp_memory.add(DecisionEntry(tags=["tag1"]))
        result = tmp_memory.get_by_tag("tag_inexistente")
        assert result == []

    def test_get_by_run_id(self, tmp_memory):
        e1 = DecisionEntry(run_id="run-001")
        e2 = DecisionEntry(run_id="run-002")
        e3 = DecisionEntry(run_id="run-001")
        tmp_memory.add(e1)
        tmp_memory.add(e2)
        tmp_memory.add(e3)
        result = tmp_memory.get_by_run_id("run-001")
        assert len(result) == 2

    def test_get_pending_outcome(self, tmp_memory):
        e1 = DecisionEntry(context="No outcome")
        e2 = DecisionEntry(context="Has outcome", outcome="vitória")
        tmp_memory.add(e1)
        tmp_memory.add(e2)
        pending = tmp_memory.get_pending_outcome()
        assert len(pending) == 1
        assert pending[0].context == "No outcome"

    def test_get_pending_feedback(self, tmp_memory):
        e1 = DecisionEntry(context="No feedback")
        e2 = DecisionEntry(context="Has feedback", feedback="Boa decisão")
        tmp_memory.add(e1)
        tmp_memory.add(e2)
        pending = tmp_memory.get_pending_feedback()
        assert len(pending) == 1

    def test_update_outcome(self, tmp_memory):
        entry = DecisionEntry(context="Test")
        tmp_memory.add(entry)
        updated = tmp_memory.update_outcome(entry.entry_id, "vitória", "Gol no final")
        assert updated is not None
        assert updated.outcome == "vitória"
        assert updated.outcome_notes == "Gol no final"

    def test_update_outcome_not_found(self, tmp_memory):
        result = tmp_memory.update_outcome("id-inexistente", "vitória")
        assert result is None

    def test_update_feedback(self, tmp_memory):
        entry = DecisionEntry(context="Test")
        tmp_memory.add(entry)
        updated = tmp_memory.update_feedback(
            entry.entry_id, "Decisão correta", "Analista João"
        )
        assert updated is not None
        assert updated.feedback == "Decisão correta"
        assert updated.human_reviewer == "Analista João"

    def test_update_feedback_not_found(self, tmp_memory):
        result = tmp_memory.update_feedback("id-inexistente", "feedback", "reviewer")
        assert result is None

    def test_persistence_across_instances(self, tmp_path):
        """Dados devem persistir entre instâncias diferentes."""
        memory_file = tmp_path / "persist_test.json"
        m1 = DecisionMemory(memory_file=memory_file)
        entry = DecisionEntry(context="Persistência", decision_taken="Decisão A")
        m1.add(entry)

        # Nova instância lendo o mesmo arquivo
        m2 = DecisionMemory(memory_file=memory_file)
        assert m2.count() == 1
        all_entries = m2.get_all()
        assert all_entries[0].context == "Persistência"

    def test_summary_structure(self, tmp_memory):
        tmp_memory.add(DecisionEntry(outcome="vitória"))
        tmp_memory.add(DecisionEntry(feedback="OK", human_reviewer="João"))
        tmp_memory.add(DecisionEntry())
        summary = tmp_memory.summary()
        assert "total_entries" in summary
        assert "with_outcome" in summary
        assert "without_outcome" in summary
        assert "with_feedback" in summary
        assert "without_feedback" in summary
        assert summary["total_entries"] == 3

    def test_summary_counts_correctly(self, tmp_memory):
        tmp_memory.add(DecisionEntry(outcome="vitória"))
        tmp_memory.add(DecisionEntry())
        summary = tmp_memory.summary()
        assert summary["with_outcome"] == 1
        assert summary["without_outcome"] == 1

    def test_corrupted_file_loads_empty(self, tmp_path):
        """Arquivo corrompido deve resultar em memória vazia, não exceção."""
        memory_file = tmp_path / "corrupted.json"
        memory_file.write_text("{ invalid json }", encoding="utf-8")
        memory = DecisionMemory(memory_file=memory_file)
        assert memory.count() == 0

    def test_nonexistent_file_loads_empty(self, tmp_path):
        """Arquivo inexistente deve resultar em memória vazia."""
        memory_file = tmp_path / "nonexistent.json"
        memory = DecisionMemory(memory_file=memory_file)
        assert memory.count() == 0

    def test_add_creates_file(self, tmp_path):
        """Adicionar entrada deve criar o arquivo de persistência."""
        memory_file = tmp_path / "new_memory.json"
        assert not memory_file.exists()
        memory = DecisionMemory(memory_file=memory_file)
        memory.add(DecisionEntry(context="Test"))
        assert memory_file.exists()

    def test_file_is_valid_json(self, tmp_path):
        """Arquivo de persistência deve ser JSON válido."""
        memory_file = tmp_path / "valid_json.json"
        memory = DecisionMemory(memory_file=memory_file)
        memory.add(DecisionEntry(context="Test"))
        data = json.loads(memory_file.read_text(encoding="utf-8"))
        assert "entries" in data
        assert isinstance(data["entries"], list)
