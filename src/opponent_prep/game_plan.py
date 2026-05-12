"""
game_plan.py — Gerador de Plano de Jogo Pré-Partida para o SPFC Champion Decision OS.

Responsabilidade:
    Gerar um plano de jogo estruturado combinando:
    - Análise do adversário (OpponentAnalysisReport)
    - Base de conhecimento do SPFC (KnowledgeBase)
    - Contexto da partida (Match)

Regras constitucionais:
    - Não inventar dados: o plano é derivado dos dados fornecidos.
    - Separar fato, inferência e recomendação.
    - Simulações são cenários, não certezas.
    - Decisão final é sempre humana.
    - Confiança explícita em cada seção.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.core.football_models import Match
from src.opponent_prep.opponent_analyzer import OpponentAnalysisReport


# ---------------------------------------------------------------------------
# GamePlanSection
# ---------------------------------------------------------------------------

@dataclass
class GamePlanSection:
    """
    Seção de um plano de jogo.

    Campos:
        title: Título da seção.
        phase: Fase do jogo a que se refere ("defensive" | "offensive" | "transition" | "set_piece" | "general").
        instructions: Lista de instruções táticas.
        rationale: Justificativa baseada na análise do adversário.
        priority: Prioridade ("high" | "medium" | "low").
        confidence: Confiança da recomendação (0.0 a 1.0).
    """
    title: str = ""
    phase: str = "general"
    instructions: List[str] = field(default_factory=list)
    rationale: str = ""
    priority: str = "medium"
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "phase": self.phase,
            "instructions": self.instructions,
            "rationale": self.rationale,
            "priority": self.priority,
            "confidence": self.confidence,
        }


# ---------------------------------------------------------------------------
# GamePlan
# ---------------------------------------------------------------------------

@dataclass
class GamePlan:
    """
    Plano de jogo completo para uma partida.

    Campos:
        plan_id: Identificador único do plano.
        created_at: Data/hora de criação.
        match_context: Contexto da partida.
        opponent_id: ID do adversário.
        opponent_name: Nome do adversário.
        sections: Seções do plano de jogo.
        key_messages: Mensagens-chave para a equipe (máx 5).
        risk_flags: Riscos identificados.
        contingency_notes: Notas de contingência para ajustes em jogo.
        overall_confidence: Confiança geral do plano (0.0 a 1.0).
        disclaimer: Aviso obrigatório sobre a natureza do plano.
        data_completeness: Completude dos dados base (0.0 a 1.0).
    """
    plan_id: str = field(
        default_factory=lambda: f"plan-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    )
    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )
    match_context: str = ""
    opponent_id: str = "unknown"
    opponent_name: str = "Adversário"
    sections: List[GamePlanSection] = field(default_factory=list)
    key_messages: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    contingency_notes: List[str] = field(default_factory=list)
    overall_confidence: float = 0.0
    disclaimer: str = (
        "Este plano é uma ferramenta de apoio à decisão. "
        "Não substitui o julgamento da comissão técnica. "
        "A decisão final é sempre humana."
    )
    data_completeness: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "created_at": self.created_at,
            "match_context": self.match_context,
            "opponent_id": self.opponent_id,
            "opponent_name": self.opponent_name,
            "sections": [s.to_dict() for s in self.sections],
            "key_messages": self.key_messages,
            "risk_flags": self.risk_flags,
            "contingency_notes": self.contingency_notes,
            "overall_confidence": self.overall_confidence,
            "disclaimer": self.disclaimer,
            "data_completeness": self.data_completeness,
        }


# ---------------------------------------------------------------------------
# GamePlanGenerator
# ---------------------------------------------------------------------------

class GamePlanGenerator:
    """
    Gerador de plano de jogo pré-partida.

    Combina a análise do adversário com os princípios táticos do SPFC
    para gerar um plano estruturado por fase de jogo.

    Não inventa dados: seções sem dados suficientes são marcadas com
    confiança baixa e instruções de coleta de informação adicional.
    """

    def generate(
        self,
        analysis: OpponentAnalysisReport,
        match: Optional[Match] = None,
        spfc_principles: Optional[List[str]] = None,
    ) -> GamePlan:
        """
        Gera um plano de jogo a partir da análise do adversário.

        Args:
            analysis: Relatório de análise do adversário.
            match: Contexto da partida (opcional).
            spfc_principles: Princípios inegociáveis do SPFC (opcional).

        Returns:
            GamePlan com seções estruturadas por fase de jogo.
        """
        match_context = self._build_match_context(match)
        sections = []

        sections.append(self._build_defensive_section(analysis))
        sections.append(self._build_offensive_section(analysis))
        sections.append(self._build_transition_section(analysis))
        sections.append(self._build_set_piece_section(analysis))

        if spfc_principles:
            sections.append(self._build_principles_section(spfc_principles))

        key_messages = self._build_key_messages(analysis)
        risk_flags = self._build_risk_flags(analysis)
        contingency = self._build_contingency_notes(analysis)
        confidence = self._calculate_confidence(analysis)

        return GamePlan(
            match_context=match_context,
            opponent_id=analysis.opponent_id,
            opponent_name=analysis.opponent_name,
            sections=sections,
            key_messages=key_messages,
            risk_flags=risk_flags,
            contingency_notes=contingency,
            overall_confidence=confidence,
            data_completeness=analysis.data_completeness,
        )

    # ------------------------------------------------------------------
    # Seção Defensiva
    # ------------------------------------------------------------------

    def _build_defensive_section(self, analysis: OpponentAnalysisReport) -> GamePlanSection:
        """Constrói a seção de organização defensiva."""
        instructions = []
        pressing = analysis.pressing_analysis

        if pressing.intensity == "high":
            instructions.extend([
                "Preparar saída de bola sob pressão intensa.",
                "Goleiro deve ser opção de passe seguro na construção.",
                "Laterais fecham no centro quando adversário pressiona.",
                "Bola longa para o segundo homem como válvula de escape.",
            ])
        elif pressing.intensity == "medium":
            instructions.extend([
                "Construção paciente com triangulações no meio-campo.",
                "Explorar o espaço entre as linhas adversárias.",
                "Laterais avançam quando o pressing adversário recua.",
            ])
        elif pressing.intensity == "low":
            instructions.extend([
                "Construção com paciência — adversário em bloco baixo.",
                "Circular a bola para abrir espaços.",
                "Evitar passes arriscados na saída de bola.",
            ])
        else:
            instructions.append(
                "Dados de pressing insuficientes. "
                "Adaptar na observação dos primeiros 15 minutos."
            )

        rationale = (
            f"Adversário com pressing de intensidade {pressing.intensity}. "
            f"{pressing.explanation}"
            if pressing.intensity != "unknown"
            else "Dados insuficientes para análise de pressing."
        )

        return GamePlanSection(
            title="Organização Defensiva",
            phase="defensive",
            instructions=instructions,
            rationale=rationale,
            priority="high",
            confidence=pressing.confidence,
        )

    # ------------------------------------------------------------------
    # Seção Ofensiva
    # ------------------------------------------------------------------

    def _build_offensive_section(self, analysis: OpponentAnalysisReport) -> GamePlanSection:
        """Constrói a seção de organização ofensiva."""
        instructions = []
        zone_vulns = analysis.zone_vulnerabilities

        if zone_vulns:
            # Priorizar zonas críticas e altas
            priority_zones = sorted(
                zone_vulns,
                key=lambda z: {"critical": 0, "high": 1, "moderate": 2, "low": 3}.get(z.severity, 4)
            )
            for zone in priority_zones[:3]:
                instructions.append(
                    f"Corredor {zone.corridor.title()}: {zone.exploitation_method}"
                )
        else:
            instructions.append(
                "Nenhuma vulnerabilidade de zona identificada. "
                "Manter jogo posicional e aguardar erros adversários."
            )

        # Adicionar instrução baseada no pressing
        pressing = analysis.pressing_analysis
        if pressing.vulnerability_to_buildup:
            instructions.append(pressing.vulnerability_to_buildup)

        rationale = (
            f"{len(zone_vulns)} zona(s) de vulnerabilidade identificada(s). "
            "Explorar os corredores com maior probabilidade de sucesso."
            if zone_vulns
            else "Análise ofensiva baseada no modelo de jogo do SPFC."
        )

        avg_confidence = (
            sum(z.confidence for z in zone_vulns) / len(zone_vulns)
            if zone_vulns else 0.3
        )

        return GamePlanSection(
            title="Organização Ofensiva",
            phase="offensive",
            instructions=instructions,
            rationale=rationale,
            priority="high" if zone_vulns else "medium",
            confidence=round(avg_confidence, 2),
        )

    # ------------------------------------------------------------------
    # Seção de Transição
    # ------------------------------------------------------------------

    def _build_transition_section(self, analysis: OpponentAnalysisReport) -> GamePlanSection:
        """Constrói a seção de transições."""
        instructions = []
        trans_vulns = analysis.transition_vulnerabilities

        if trans_vulns:
            for tv in trans_vulns:
                instructions.append(
                    f"{tv.type.replace('_', ' ').title()}: {tv.description} "
                    f"(Janela: {tv.exploitation_window})"
                )
        else:
            instructions.extend([
                "Transição defensiva: recuperar posição imediatamente após perda.",
                "Transição ofensiva: progredir rapidamente quando recuperar a bola.",
            ])

        rationale = (
            f"{len(trans_vulns)} vulnerabilidade(s) em transição identificada(s)."
            if trans_vulns
            else "Dados insuficientes para análise de transição."
        )

        avg_confidence = (
            sum(t.confidence for t in trans_vulns) / len(trans_vulns)
            if trans_vulns else 0.3
        )

        return GamePlanSection(
            title="Transições",
            phase="transition",
            instructions=instructions,
            rationale=rationale,
            priority="high" if trans_vulns else "medium",
            confidence=round(avg_confidence, 2),
        )

    # ------------------------------------------------------------------
    # Seção de Bola Parada
    # ------------------------------------------------------------------

    def _build_set_piece_section(self, analysis: OpponentAnalysisReport) -> GamePlanSection:
        """Constrói a seção de bola parada."""
        sp = analysis.set_piece_analysis
        instructions = []

        if sp.recommended_defensive_setup:
            instructions.append(f"Defensiva: {sp.recommended_defensive_setup}")

        if sp.recommended_offensive_approach:
            instructions.append(f"Ofensiva: {sp.recommended_offensive_approach}")

        if sp.key_takers_assessment:
            instructions.append(sp.key_takers_assessment)

        if sp.key_targets_assessment:
            instructions.append(sp.key_targets_assessment)

        if not instructions:
            instructions.append(
                "Dados de bola parada insuficientes. "
                "Revisar vídeo de escanteios e faltas das últimas 3 partidas."
            )

        rationale = (
            f"{len(sp.offensive_threats)} ameaça(s) ofensiva(s) identificada(s). "
            f"{len(sp.defensive_weaknesses)} fraqueza(s) defensiva(s) identificada(s)."
        )

        return GamePlanSection(
            title="Bola Parada",
            phase="set_piece",
            instructions=instructions,
            rationale=rationale,
            priority="medium",
            confidence=sp.confidence,
        )

    # ------------------------------------------------------------------
    # Seção de Princípios
    # ------------------------------------------------------------------

    def _build_principles_section(self, principles: List[str]) -> GamePlanSection:
        """Constrói a seção de princípios inegociáveis do SPFC."""
        return GamePlanSection(
            title="Princípios Inegociáveis SPFC",
            phase="general",
            instructions=principles,
            rationale=(
                "Independentemente do adversário, estes princípios "
                "devem ser mantidos em todas as situações de jogo."
            ),
            priority="high",
            confidence=1.0,
        )

    # ------------------------------------------------------------------
    # Key Messages
    # ------------------------------------------------------------------

    def _build_key_messages(self, analysis: OpponentAnalysisReport) -> List[str]:
        """Constrói as mensagens-chave para a equipe (máx 5)."""
        messages = []

        # Mensagem sobre ameaça geral
        threat_messages = {
            "critical": "Adversário de alto risco. Máxima atenção defensiva.",
            "high": "Adversário perigoso. Equilíbrio entre ataque e defesa.",
            "moderate": "Adversário de nível médio. Explorar vulnerabilidades identificadas.",
            "low": "Adversário com pontos fracos claros. Aproveitar as oportunidades.",
            "unknown": "Adversário com dados limitados. Adaptar nos primeiros 15 minutos.",
        }
        messages.append(
            threat_messages.get(analysis.overall_threat_level, "Manter o modelo de jogo.")
        )

        # Mensagem sobre pressing
        pressing = analysis.pressing_analysis
        if pressing.intensity == "high":
            messages.append("Pressing alto: manter calma na saída de bola.")
        elif pressing.intensity == "low":
            messages.append("Adversário em bloco baixo: paciência para abrir espaços.")

        # Mensagem sobre zona prioritária
        priority_zones = [z for z in analysis.zone_vulnerabilities if z.severity in ("critical", "high")]
        if priority_zones:
            zone = priority_zones[0]
            messages.append(
                f"Explorar corredor {zone.corridor}: {zone.exploitation_method}"
            )

        # Mensagem sobre bola parada
        if analysis.set_piece_analysis.key_takers_assessment:
            messages.append("Atenção especial aos cobradores de bola parada adversários.")

        # Mensagem de confiança nos dados
        if analysis.data_completeness < 0.5:
            messages.append(
                "Dados limitados: adaptar o plano conforme o jogo evolui."
            )

        return messages[:5]

    # ------------------------------------------------------------------
    # Risk Flags
    # ------------------------------------------------------------------

    def _build_risk_flags(self, analysis: OpponentAnalysisReport) -> List[str]:
        """Identifica os riscos principais do plano."""
        flags = []

        if analysis.data_completeness < 0.4:
            flags.append(
                f"Baixa completude de dados ({analysis.data_completeness:.0%}): "
                "análise pode não refletir o padrão atual do adversário."
            )

        if analysis.source_matches_count < 3:
            flags.append(
                f"Apenas {analysis.source_matches_count} partida(s) analisada(s): "
                "amostra insuficiente para padrões confiáveis."
            )

        pressing = analysis.pressing_analysis
        if pressing.intensity == "high" and pressing.confidence < 0.5:
            flags.append(
                "Pressing alto identificado com baixa confiança: "
                "preparar para ambos os cenários (pressing alto e médio)."
            )

        if analysis.overall_threat_level in ("critical", "high"):
            flags.append(
                f"Adversário de ameaça {analysis.overall_threat_level}: "
                "risco elevado de sofrer gols em transição."
            )

        return flags

    # ------------------------------------------------------------------
    # Contingency Notes
    # ------------------------------------------------------------------

    def _build_contingency_notes(self, analysis: OpponentAnalysisReport) -> List[str]:
        """Constrói notas de contingência para ajustes em jogo."""
        notes = []

        pressing = analysis.pressing_analysis
        if pressing.intensity == "high":
            notes.append(
                "Se o pressing adversário for eficaz: "
                "mudar para bola longa e segunda bola no meio-campo."
            )

        zone_vulns = analysis.zone_vulnerabilities
        if zone_vulns:
            notes.append(
                "Se as vulnerabilidades de zona forem corrigidas: "
                "mudar o corredor de ataque principal."
            )

        if analysis.overall_threat_level in ("critical", "high"):
            notes.append(
                "Se o adversário abrir vantagem: "
                "considerar mudança para 4-2-3-1 para mais presença ofensiva."
            )

        notes.append(
            "Se o placar estiver favorável nos últimos 15 minutos: "
            "recuar o bloco e priorizar a organização defensiva."
        )

        return notes

    # ------------------------------------------------------------------
    # Confidence
    # ------------------------------------------------------------------

    def _calculate_confidence(self, analysis: OpponentAnalysisReport) -> float:
        """Calcula a confiança geral do plano."""
        weights = {
            "pressing": 0.3,
            "zones": 0.3,
            "transitions": 0.2,
            "set_pieces": 0.2,
        }

        pressing_conf = analysis.pressing_analysis.confidence
        zones_conf = (
            sum(z.confidence for z in analysis.zone_vulnerabilities) / len(analysis.zone_vulnerabilities)
            if analysis.zone_vulnerabilities else 0.0
        )
        trans_conf = (
            sum(t.confidence for t in analysis.transition_vulnerabilities) / len(analysis.transition_vulnerabilities)
            if analysis.transition_vulnerabilities else 0.0
        )
        sp_conf = analysis.set_piece_analysis.confidence

        overall = (
            pressing_conf * weights["pressing"]
            + zones_conf * weights["zones"]
            + trans_conf * weights["transitions"]
            + sp_conf * weights["set_pieces"]
        )

        return round(min(overall, 1.0), 2)

    # ------------------------------------------------------------------
    # Match Context
    # ------------------------------------------------------------------

    def _build_match_context(self, match: Optional[Match]) -> str:
        """Constrói o contexto da partida para o plano."""
        if match is None:
            return "Contexto da partida não especificado."

        parts = []
        if match.home_team and match.away_team:
            parts.append(f"{match.home_team} vs {match.away_team}")
        if match.competition and match.competition != "unknown":
            parts.append(match.competition)
        if match.round and match.round != "unknown":
            parts.append(f"Rodada/Fase: {match.round}")
        if match.date:
            parts.append(f"Data: {match.date}")
        if match.venue and match.venue != "unknown":
            parts.append(f"Local: {match.venue}")

        return " | ".join(parts) if parts else "Contexto da partida não especificado."
