"""
Testes do Artifact Store — SPFC Champion Decision OS.

Categoria: Pipeline
Valida: carregamento de artefatos, demos, rejeição de payload inválido.
"""
import json
import tempfile
from pathlib import Path

import pytest

from src.core.artifact_store import ArtifactStore
from src.core.models import RunStatus


class TestArtifactStoreWithNoArtifacts:
    """Testes do ArtifactStore quando não há artefatos reais."""

    def test_list_runs_returns_demos_when_dir_missing(self):
        """Garante que runs de demo são retornadas quando o diretório não existe."""
        store = ArtifactStore(artifacts_dir=Path("/nonexistent/path"))
        runs = store.list_runs(include_demo=True)
        assert len(runs) > 0

    def test_list_runs_returns_empty_when_no_demo_and_dir_missing(self):
        """Garante que lista vazia é retornada quando demos são desabilitadas e diretório não existe."""
        store = ArtifactStore(artifacts_dir=Path("/nonexistent/path"))
        runs = store.list_runs(include_demo=False)
        assert runs == []

    def test_demo_runs_have_required_fields(self):
        """Garante que todas as runs de demo têm os campos obrigatórios preenchidos."""
        store = ArtifactStore(artifacts_dir=Path("/nonexistent/path"))
        runs = store.list_runs(include_demo=True)
        for run in runs:
            assert run.run_id is not None
            assert run.name != ""
            assert run.module != ""
            assert run.status is not None
            assert run.confidence is not None

    def test_demo_runs_are_tagged_as_fixture(self):
        """Garante que as runs de demo são marcadas com a tag 'fixture'."""
        store = ArtifactStore(artifacts_dir=Path("/nonexistent/path"))
        runs = store.list_runs(include_demo=True)
        for run in runs:
            assert "fixture" in run.tags, (
                f"Run '{run.run_id}' não tem tag 'fixture'. "
                "Runs de demo devem ser claramente identificadas."
            )


class TestArtifactStoreGetRun:
    """Testes do método get_run."""

    def test_get_demo_run_returns_detail(self):
        """Garante que get_run retorna detalhe para IDs de demo conhecidos."""
        store = ArtifactStore(artifacts_dir=Path("/nonexistent/path"))
        detail = store.get_run("demo-001")
        assert detail is not None
        assert detail.summary.run_id == "demo-001"

    def test_get_unknown_run_returns_none(self):
        """Garante que get_run retorna None para IDs desconhecidos."""
        store = ArtifactStore(artifacts_dir=Path("/nonexistent/path"))
        result = store.get_run("run-id-que-nao-existe-xyz-999")
        assert result is None

    def test_demo_detail_has_explanation(self):
        """
        Garante que runs de demo têm explicação preenchida.
        Princípio: Explicabilidade obrigatória.
        """
        store = ArtifactStore(artifacts_dir=Path("/nonexistent/path"))
        detail = store.get_run("demo-001")
        assert detail is not None
        assert detail.explanation != "", (
            "Toda run deve ter uma explicação. "
            "Princípio 6: Explicabilidade obrigatória."
        )

    def test_failed_demo_has_no_recommendations(self):
        """
        Garante que uma run com status FAILED não tem recomendações inventadas.
        Princípio: Não inventar dados.
        """
        store = ArtifactStore(artifacts_dir=Path("/nonexistent/path"))
        detail = store.get_run("demo-003")
        assert detail is not None
        assert detail.summary.status == RunStatus.FAILED
        assert detail.recommendations == [], (
            "Run com FAILED não deve ter recomendações geradas. "
            "Princípio: Não inventar dados."
        )


class TestArtifactStoreWithRealFiles:
    """Testes do ArtifactStore com arquivos reais em diretório temporário."""

    def test_loads_valid_json_artifact(self):
        """Garante que um artefato JSON válido é carregado corretamente."""
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = {
                "summary": {
                    "run_id": "file-001",
                    "name": "Teste de Arquivo",
                    "module": "test_module",
                    "status": "completed",
                    "created_at": "2026-05-01T10:00:00",
                    "completed_at": "2026-05-01T10:05:00",
                    "confidence": "high",
                    "tags": ["test"],
                },
                "inputs": {},
                "outputs": {},
                "recommendations": [],
                "risks": [],
                "explanation": "Artefato de teste.",
                "next_actions": [],
            }
            path = Path(tmpdir) / "file-001.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")

            store = ArtifactStore(artifacts_dir=Path(tmpdir))
            runs = store.list_runs(include_demo=False)
            assert len(runs) == 1
            assert runs[0].run_id == "file-001"
            assert runs[0].name == "Teste de Arquivo"

    def test_invalid_json_is_reported_not_silenced(self):
        """
        Garante que JSON inválido é reportado como erro, não aceito silenciosamente.
        Princípio: Payload ruim não entra silenciosamente.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "bad-artifact.json"
            path.write_text("{ this is not valid json }", encoding="utf-8")

            store = ArtifactStore(artifacts_dir=Path(tmpdir))
            runs = store.list_runs(include_demo=False)

            # O arquivo inválido deve gerar uma run de erro, não ser ignorado
            assert len(runs) == 1
            assert runs[0].status == RunStatus.FAILED
            assert "load_error" in runs[0].tags

    def test_get_run_from_file(self):
        """Garante que get_run carrega corretamente um artefato de arquivo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            artifact = {
                "summary": {
                    "run_id": "file-002",
                    "name": "Get Run de Arquivo",
                    "module": "test_module",
                    "status": "completed",
                    "created_at": "2026-05-01T10:00:00",
                    "confidence": "medium",
                    "tags": [],
                },
                "inputs": {"x": 1},
                "outputs": {"y": 2},
                "recommendations": ["Recomendação de arquivo"],
                "risks": [],
                "explanation": "Explicação de arquivo.",
                "next_actions": [],
            }
            path = Path(tmpdir) / "file-002.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")

            store = ArtifactStore(artifacts_dir=Path(tmpdir))
            detail = store.get_run("file-002")
            assert detail is not None
            assert detail.summary.run_id == "file-002"
            assert detail.inputs == {"x": 1}
            assert detail.recommendations == ["Recomendação de arquivo"]
