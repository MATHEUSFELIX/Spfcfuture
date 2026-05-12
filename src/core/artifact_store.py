"""
Artifact Store — Carregador de artefatos de runs do pipeline.

Princípio: Não inventar dados. O store lê artefatos reais ou retorna lista vazia.
Princípio: Payload ruim não entra silenciosamente — erros são reportados.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from src.core.models import ConfidenceLevel, RunDetail, RunStatus, RunSummary

# Diretório padrão onde os artefatos de runs são armazenados
DEFAULT_ARTIFACTS_DIR = Path(os.environ.get("FOOTBALL_OS_ARTIFACTS", "artifacts/runs"))

# Runs de demonstração (fixtures determinísticas — não são dados reais de jogo)
DEMO_RUNS: List[RunSummary] = [
    RunSummary(
        run_id="demo-001",
        name="Demo — Análise de Cenário (Fixture)",
        module="match_intelligence",
        status=RunStatus.COMPLETED,
        created_at=datetime(2026, 5, 1, 10, 0, 0),
        completed_at=datetime(2026, 5, 1, 10, 5, 30),
        confidence=ConfidenceLevel.MEDIUM,
        tags=["demo", "fixture", "match_intelligence"],
        artifact_path=None,
    ),
    RunSummary(
        run_id="demo-002",
        name="Demo — Perfil de Elenco (Fixture)",
        module="squad_intelligence",
        status=RunStatus.COMPLETED,
        created_at=datetime(2026, 5, 2, 14, 0, 0),
        completed_at=datetime(2026, 5, 2, 14, 3, 10),
        confidence=ConfidenceLevel.HIGH,
        tags=["demo", "fixture", "squad_intelligence"],
        artifact_path=None,
    ),
    RunSummary(
        run_id="demo-003",
        name="Demo — Pipeline com Falha (Fixture)",
        module="scouting",
        status=RunStatus.FAILED,
        created_at=datetime(2026, 5, 3, 9, 0, 0),
        completed_at=None,
        confidence=ConfidenceLevel.UNKNOWN,
        tags=["demo", "fixture", "scouting", "failed"],
        artifact_path=None,
    ),
]

DEMO_DETAILS: dict = {
    "demo-001": RunDetail(
        summary=DEMO_RUNS[0],
        inputs={"scenario": "Cenário de demonstração", "source": "fixture"},
        outputs={"branches": 3, "top_branch_score": 0.72},
        recommendations=[
            "Esta é uma run de demonstração. Nenhum dado real de jogo foi utilizado.",
            "Para análises reais, forneça dados via pipeline de ingestão.",
        ],
        risks=[
            "Dados de fixture — não representam situação real de jogo.",
        ],
        explanation=(
            "Esta run é um artefato de demonstração gerado para validar o funcionamento "
            "da interface web. Nenhuma estatística, lance ou dado esportivo real foi "
            "inventado ou utilizado."
        ),
        human_feedback=None,
        next_actions=["Fornecer dados reais via pipeline de ingestão para análise efetiva."],
    ),
    "demo-002": RunDetail(
        summary=DEMO_RUNS[1],
        inputs={"team": "São Paulo FC", "season": "2026", "source": "fixture"},
        outputs={"roles_covered": 0, "role_gaps": 0, "depth_score": None},
        recommendations=[
            "Esta é uma run de demonstração. Nenhum dado real de elenco foi utilizado.",
        ],
        risks=[
            "Dados de fixture — não representam elenco real.",
        ],
        explanation=(
            "Esta run é um artefato de demonstração para o módulo Squad Intelligence. "
            "Para análise real, o pipeline de ingestão deve receber dados de elenco validados."
        ),
        human_feedback=None,
        next_actions=["Integrar dados de elenco via pipeline de ingestão."],
    ),
    "demo-003": RunDetail(
        summary=DEMO_RUNS[2],
        inputs={"target": "Fixture de falha", "source": "fixture"},
        outputs={},
        recommendations=[],
        risks=["Pipeline falhou antes de gerar recomendações."],
        explanation=(
            "Esta run de demonstração simula uma falha no pipeline de scouting. "
            "O sistema detectou o erro e registrou o status como FAILED sem aceitar "
            "payload inválido silenciosamente."
        ),
        human_feedback=None,
        next_actions=["Verificar logs de ingestão e corrigir payload de entrada."],
    ),
}


class ArtifactStore:
    """
    Carregador de artefatos de runs.

    Lê artefatos do diretório configurado ou retorna as runs de demonstração.
    Nunca inventa dados — se não há artefato, retorna lista vazia ou demo.
    """

    def __init__(self, artifacts_dir: Path = DEFAULT_ARTIFACTS_DIR) -> None:
        self.artifacts_dir = artifacts_dir

    def list_runs(self, include_demo: bool = True) -> List[RunSummary]:
        """
        Lista todos os runs disponíveis.

        Args:
            include_demo: Se True, inclui as runs de demonstração quando não há
                          artefatos reais disponíveis.

        Returns:
            Lista de RunSummary ordenada por data de criação (mais recente primeiro).
        """
        runs: List[RunSummary] = []

        if self.artifacts_dir.exists():
            for path in sorted(self.artifacts_dir.glob("*.json"), reverse=True):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    summary_data = data.get("summary", data)
                    runs.append(RunSummary.from_dict(summary_data))
                except (json.JSONDecodeError, KeyError, ValueError) as exc:
                    # Payload ruim não entra silenciosamente
                    runs.append(
                        RunSummary(
                            run_id=path.stem,
                            name=f"[ERRO ao carregar: {path.name}]",
                            module="unknown",
                            status=RunStatus.FAILED,
                            tags=["load_error"],
                        )
                    )

        if not runs and include_demo:
            return list(DEMO_RUNS)

        return runs

    def get_run(self, run_id: str) -> Optional[RunDetail]:
        """
        Retorna o detalhe de um run pelo ID.

        Args:
            run_id: Identificador único da run.

        Returns:
            RunDetail se encontrado, None caso contrário.
        """
        # Verifica demos primeiro
        if run_id in DEMO_DETAILS:
            return DEMO_DETAILS[run_id]

        # Tenta carregar do diretório de artefatos
        artifact_path = self.artifacts_dir / f"{run_id}.json"
        if artifact_path.exists():
            try:
                with open(artifact_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                summary = RunSummary.from_dict(data.get("summary", {}))
                return RunDetail(
                    summary=summary,
                    inputs=data.get("inputs", {}),
                    outputs=data.get("outputs", {}),
                    recommendations=data.get("recommendations", []),
                    risks=data.get("risks", []),
                    explanation=data.get("explanation", ""),
                    human_feedback=data.get("human_feedback"),
                    next_actions=data.get("next_actions", []),
                )
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                return None

        return None
