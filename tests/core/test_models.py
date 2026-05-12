"""
Testes de Domain Models — SPFC Champion Decision OS.

Categoria: Domain Models
Valida: serialização, defaults, validação e integridade dos modelos de domínio.
"""
from datetime import datetime

import pytest

from src.core.models import (
    ConfidenceLevel,
    RunDetail,
    RunStatus,
    RunSummary,
)


class TestRunStatus:
    """Testes para o enum RunStatus."""

    def test_all_statuses_have_string_values(self):
        """Garante que todos os status têm valores de string válidos."""
        for status in RunStatus:
            assert isinstance(status.value, str)
            assert len(status.value) > 0

    def test_status_values_are_known(self):
        """Garante que os valores de status são os esperados."""
        expected = {"pending", "running", "completed", "failed"}
        actual = {s.value for s in RunStatus}
        assert actual == expected


class TestConfidenceLevel:
    """Testes para o enum ConfidenceLevel."""

    def test_all_levels_have_string_values(self):
        """Garante que todos os níveis de confiança têm valores de string válidos."""
        for level in ConfidenceLevel:
            assert isinstance(level.value, str)

    def test_confidence_levels_are_known(self):
        """Garante que os valores de confiança são os esperados."""
        expected = {"high", "medium", "low", "unknown"}
        actual = {c.value for c in ConfidenceLevel}
        assert actual == expected


class TestRunSummary:
    """Testes para o modelo RunSummary."""

    def test_default_values_are_safe(self):
        """Garante que RunSummary tem defaults seguros e não levanta exceção."""
        run = RunSummary()
        assert run.run_id is not None
        assert len(run.run_id) > 0
        assert run.name == "Unnamed Run"
        assert run.module == "unknown"
        assert run.status == RunStatus.PENDING
        assert run.confidence == ConfidenceLevel.UNKNOWN
        assert run.tags == []
        assert run.artifact_path is None
        assert run.completed_at is None

    def test_run_id_is_unique(self):
        """Garante que dois RunSummary criados sem ID explícito têm IDs diferentes."""
        r1 = RunSummary()
        r2 = RunSummary()
        assert r1.run_id != r2.run_id

    def test_to_dict_contains_all_fields(self):
        """Garante que to_dict serializa todos os campos obrigatórios."""
        run = RunSummary(
            run_id="test-001",
            name="Teste de Serialização",
            module="match_intelligence",
            status=RunStatus.COMPLETED,
            confidence=ConfidenceLevel.HIGH,
            tags=["test", "unit"],
        )
        d = run.to_dict()
        assert d["run_id"] == "test-001"
        assert d["name"] == "Teste de Serialização"
        assert d["module"] == "match_intelligence"
        assert d["status"] == "completed"
        assert d["confidence"] == "high"
        assert d["tags"] == ["test", "unit"]
        assert "created_at" in d
        assert d["completed_at"] is None

    def test_from_dict_roundtrip(self):
        """Garante que from_dict(to_dict(run)) == run (roundtrip de serialização)."""
        original = RunSummary(
            run_id="roundtrip-001",
            name="Roundtrip Test",
            module="squad_intelligence",
            status=RunStatus.FAILED,
            confidence=ConfidenceLevel.LOW,
            tags=["roundtrip"],
        )
        restored = RunSummary.from_dict(original.to_dict())
        assert restored.run_id == original.run_id
        assert restored.name == original.name
        assert restored.module == original.module
        assert restored.status == original.status
        assert restored.confidence == original.confidence
        assert restored.tags == original.tags

    def test_from_dict_with_completed_at(self):
        """Garante que completed_at é desserializado corretamente."""
        data = {
            "run_id": "test-002",
            "name": "Com completed_at",
            "module": "scouting",
            "status": "completed",
            "created_at": "2026-05-01T10:00:00",
            "completed_at": "2026-05-01T10:05:30",
            "confidence": "medium",
            "tags": [],
        }
        run = RunSummary.from_dict(data)
        assert run.completed_at is not None
        assert run.completed_at.year == 2026

    def test_from_dict_missing_optional_fields(self):
        """Garante que campos opcionais ausentes usam defaults seguros."""
        data = {
            "run_id": "test-003",
            "created_at": "2026-05-01T10:00:00",
        }
        run = RunSummary.from_dict(data)
        assert run.name == "Unnamed Run"
        assert run.module == "unknown"
        assert run.tags == []
        assert run.artifact_path is None

    def test_invalid_status_raises(self):
        """Garante que status inválido levanta ValueError."""
        with pytest.raises(ValueError):
            RunSummary.from_dict({
                "run_id": "bad",
                "status": "invalid_status",
                "created_at": "2026-01-01T00:00:00",
            })

    def test_invalid_confidence_raises(self):
        """Garante que confidence inválida levanta ValueError."""
        with pytest.raises(ValueError):
            RunSummary.from_dict({
                "run_id": "bad",
                "confidence": "super_high",
                "created_at": "2026-01-01T00:00:00",
            })


class TestRunDetail:
    """Testes para o modelo RunDetail."""

    def test_default_values_are_safe(self):
        """Garante que RunDetail tem defaults seguros."""
        detail = RunDetail()
        assert detail.summary is not None
        assert detail.inputs == {}
        assert detail.outputs == {}
        assert detail.recommendations == []
        assert detail.risks == []
        assert detail.explanation == ""
        assert detail.human_feedback is None
        assert detail.next_actions == []

    def test_to_dict_contains_all_sections(self):
        """Garante que to_dict inclui todas as seções obrigatórias."""
        detail = RunDetail(
            summary=RunSummary(run_id="detail-001"),
            inputs={"key": "value"},
            outputs={"score": 0.8},
            recommendations=["Recomendação 1"],
            risks=["Risco 1"],
            explanation="Explicação de teste.",
            next_actions=["Ação 1"],
        )
        d = detail.to_dict()
        assert "summary" in d
        assert "inputs" in d
        assert "outputs" in d
        assert "recommendations" in d
        assert "risks" in d
        assert "explanation" in d
        assert "human_feedback" in d
        assert "next_actions" in d
        assert d["inputs"] == {"key": "value"}
        assert d["recommendations"] == ["Recomendação 1"]

    def test_explanation_is_not_invented(self):
        """
        Garante que a explicação não é gerada automaticamente — deve ser
        fornecida explicitamente ou permanecer vazia.
        Princípio: Não inventar dados.
        """
        detail = RunDetail()
        assert detail.explanation == ""
