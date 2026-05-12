"""
Domain models for SPFC Champion Decision OS.

Princípio: Todo modelo tem validação, serialização, defaults seguros e erro claro.
Princípio: Não inventar dados. Modelos são estruturas, não fontes de dados.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class RunStatus(str, Enum):
    """Status possíveis de uma execução (run) do pipeline."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ConfidenceLevel(str, Enum):
    """Nível de confiança de um resultado ou recomendação."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class RunSummary:
    """
    Resumo de uma execução do pipeline de decisão.

    Atributos:
        run_id: Identificador único da execução.
        name: Nome descritivo do cenário ou análise.
        module: Módulo do sistema que gerou o run (ex: 'match_intelligence').
        status: Status atual da execução.
        created_at: Timestamp de criação.
        completed_at: Timestamp de conclusão (None se ainda em andamento).
        confidence: Nível de confiança do resultado.
        tags: Lista de tags para categorização.
        artifact_path: Caminho para o artefato de saída (relatório, JSON, etc.).
    """
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed Run"
    module: str = "unknown"
    status: RunStatus = RunStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    confidence: ConfidenceLevel = ConfidenceLevel.UNKNOWN
    tags: List[str] = field(default_factory=list)
    artifact_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o RunSummary para dicionário."""
        return {
            "run_id": self.run_id,
            "name": self.name,
            "module": self.module,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "confidence": self.confidence.value,
            "tags": self.tags,
            "artifact_path": self.artifact_path,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RunSummary":
        """Desserializa um RunSummary a partir de dicionário."""
        return cls(
            run_id=data.get("run_id", str(uuid.uuid4())),
            name=data.get("name", "Unnamed Run"),
            module=data.get("module", "unknown"),
            status=RunStatus(data.get("status", RunStatus.PENDING.value)),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.utcnow(),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            confidence=ConfidenceLevel(data.get("confidence", ConfidenceLevel.UNKNOWN.value)),
            tags=data.get("tags", []),
            artifact_path=data.get("artifact_path"),
        )


@dataclass
class RunDetail:
    """
    Detalhe completo de uma execução do pipeline.

    Atributos:
        summary: Resumo da execução.
        inputs: Entradas fornecidas ao pipeline.
        outputs: Saídas geradas pelo pipeline.
        recommendations: Lista de recomendações geradas.
        risks: Lista de riscos identificados.
        explanation: Explicação textual do resultado.
        human_feedback: Feedback humano registrado (se houver).
        next_actions: Próximas ações sugeridas.
    """
    summary: RunSummary = field(default_factory=RunSummary)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    explanation: str = ""
    human_feedback: Optional[str] = None
    next_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o RunDetail para dicionário."""
        return {
            "summary": self.summary.to_dict(),
            "inputs": self.inputs,
            "outputs": self.outputs,
            "recommendations": self.recommendations,
            "risks": self.risks,
            "explanation": self.explanation,
            "human_feedback": self.human_feedback,
            "next_actions": self.next_actions,
        }
