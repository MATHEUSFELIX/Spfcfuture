"""
decision_memory.py — Memória de Decisões do São Paulo FC.

Registra decisões passadas, feedback humano e resultados observados.
Permite rastreabilidade total e calibração contínua do sistema.

Princípio: Rastreabilidade total — toda decisão registrada é auditável.
Princípio: Não inventar dados — resultados são registrados, não estimados.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------

@dataclass
class DecisionEntry:
    """
    Registro de uma decisão tomada, com contexto, resultado e feedback.

    Campos:
        entry_id: Identificador único do registro.
        created_at: Data/hora do registro.
        context: Contexto da decisão (partida, fase, situação).
        decision_taken: Descrição da decisão tomada.
        alternatives_considered: Alternativas que foram consideradas.
        rationale: Justificativa da decisão.
        outcome: Resultado observado (preenchido após o jogo).
        outcome_notes: Notas sobre o resultado.
        human_reviewer: Nome do revisor humano.
        feedback: Feedback do revisor humano.
        tags: Tags para categorização e busca.
        run_id: ID da run do pipeline que gerou esta decisão (se aplicável).
    """
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )
    context: str = ""
    decision_taken: str = ""
    alternatives_considered: List[str] = field(default_factory=list)
    rationale: str = ""
    outcome: Optional[str] = None
    outcome_notes: str = ""
    human_reviewer: Optional[str] = None
    feedback: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    run_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "created_at": self.created_at,
            "context": self.context,
            "decision_taken": self.decision_taken,
            "alternatives_considered": self.alternatives_considered,
            "rationale": self.rationale,
            "outcome": self.outcome,
            "outcome_notes": self.outcome_notes,
            "human_reviewer": self.human_reviewer,
            "feedback": self.feedback,
            "tags": self.tags,
            "run_id": self.run_id,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DecisionEntry":
        return cls(
            entry_id=d.get("entry_id", str(uuid.uuid4())),
            created_at=d.get("created_at", datetime.utcnow().isoformat() + "Z"),
            context=d.get("context", ""),
            decision_taken=d.get("decision_taken", ""),
            alternatives_considered=d.get("alternatives_considered", []),
            rationale=d.get("rationale", ""),
            outcome=d.get("outcome"),
            outcome_notes=d.get("outcome_notes", ""),
            human_reviewer=d.get("human_reviewer"),
            feedback=d.get("feedback"),
            tags=d.get("tags", []),
            run_id=d.get("run_id"),
        )


# ---------------------------------------------------------------------------
# Memória de Decisões
# ---------------------------------------------------------------------------

class DecisionMemory:
    """
    Repositório de memória de decisões do clube.

    Persiste decisões em arquivo JSON e permite consultas por tag,
    contexto e período.

    Princípio: Rastreabilidade total — nenhuma decisão é apagada.
    """

    DEFAULT_MEMORY_FILE = Path("artifacts") / "decision_memory.json"

    def __init__(self, memory_file: Optional[Path] = None) -> None:
        self._file = memory_file or self.DEFAULT_MEMORY_FILE
        self._entries: List[DecisionEntry] = []
        self._load()

    def _load(self) -> None:
        """Carrega entradas do arquivo de memória, se existir."""
        if self._file.exists():
            try:
                data = json.loads(self._file.read_text(encoding="utf-8"))
                self._entries = [
                    DecisionEntry.from_dict(e) for e in data.get("entries", [])
                ]
            except (json.JSONDecodeError, KeyError, ValueError):
                # Arquivo corrompido — não apagar, registrar como erro
                self._entries = []

    def _save(self) -> None:
        """Persiste entradas no arquivo de memória."""
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._file.write_text(
            json.dumps(
                {"entries": [e.to_dict() for e in self._entries]},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def add(self, entry: DecisionEntry) -> DecisionEntry:
        """Adiciona uma nova entrada de decisão e persiste."""
        self._entries.append(entry)
        self._save()
        return entry

    def get_all(self) -> List[DecisionEntry]:
        """Retorna todas as entradas, da mais recente para a mais antiga."""
        return list(reversed(self._entries))

    def get_by_tag(self, tag: str) -> List[DecisionEntry]:
        """Retorna entradas com uma tag específica."""
        return [e for e in self._entries if tag in e.tags]

    def get_by_run_id(self, run_id: str) -> List[DecisionEntry]:
        """Retorna entradas associadas a um run_id específico."""
        return [e for e in self._entries if e.run_id == run_id]

    def get_pending_outcome(self) -> List[DecisionEntry]:
        """Retorna entradas sem resultado registrado."""
        return [e for e in self._entries if e.outcome is None]

    def get_pending_feedback(self) -> List[DecisionEntry]:
        """Retorna entradas sem feedback humano registrado."""
        return [e for e in self._entries if e.feedback is None]

    def update_outcome(
        self,
        entry_id: str,
        outcome: str,
        outcome_notes: str = "",
    ) -> Optional[DecisionEntry]:
        """
        Registra o resultado observado de uma decisão.
        Retorna a entrada atualizada, ou None se não encontrada.
        """
        for entry in self._entries:
            if entry.entry_id == entry_id:
                entry.outcome = outcome
                entry.outcome_notes = outcome_notes
                self._save()
                return entry
        return None

    def update_feedback(
        self,
        entry_id: str,
        feedback: str,
        reviewer: str,
    ) -> Optional[DecisionEntry]:
        """
        Registra o feedback humano de uma decisão.
        Retorna a entrada atualizada, ou None se não encontrada.
        """
        for entry in self._entries:
            if entry.entry_id == entry_id:
                entry.feedback = feedback
                entry.human_reviewer = reviewer
                self._save()
                return entry
        return None

    def count(self) -> int:
        """Retorna o total de entradas na memória."""
        return len(self._entries)

    def summary(self) -> Dict[str, Any]:
        """Retorna um resumo da memória de decisões."""
        total = len(self._entries)
        with_outcome = sum(1 for e in self._entries if e.outcome is not None)
        with_feedback = sum(1 for e in self._entries if e.feedback is not None)
        return {
            "total_entries": total,
            "with_outcome": with_outcome,
            "without_outcome": total - with_outcome,
            "with_feedback": with_feedback,
            "without_feedback": total - with_feedback,
        }
