"""
opponent_analyzer.py — Analisador de Adversários para o SPFC Champion Decision OS.

Responsabilidade:
    Analisar o perfil de um adversário e gerar um relatório estruturado com:
    - Análise de pressing e linha defensiva
    - Zonas de vulnerabilidade por corredor
    - Vulnerabilidades em transição
    - Perfil de bola parada
    - Alertas táticos
    - Avaliação geral de ameaça

Regras constitucionais:
    - Não inventar dados: toda análise é baseada nos dados fornecidos.
    - Separar fato (dados do perfil), inferência (análise) e recomendação (plano).
    - Confiança explícita: toda análise tem um campo de confiança.
    - Dados ausentes são reportados, não preenchidos com suposições.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.core.football_models import OpponentProfile, SetPieceProfile


# ---------------------------------------------------------------------------
# Enums e constantes
# ---------------------------------------------------------------------------

PRESSING_INTENSITY_LEVELS = ("high", "medium", "low", "unknown")
DEFENSIVE_LINE_LEVELS = ("high", "medium", "low", "unknown")
THREAT_LEVELS = ("critical", "high", "moderate", "low", "unknown")
CORRIDOR_LABELS = ("left", "center", "right")


# ---------------------------------------------------------------------------
# Resultado: PressingAnalysis
# ---------------------------------------------------------------------------

@dataclass
class PressingAnalysis:
    """
    Análise do sistema de pressing do adversário.

    Campos:
        intensity: Intensidade do pressing ("high" | "medium" | "low" | "unknown").
        trigger_zones: Zonas onde o pressing é ativado (ex: ["defensive_third"]).
        defensive_line: Altura da linha defensiva.
        compactness: Compactidade do bloco defensivo.
        recovery_speed: Velocidade de recuperação após perda.
        vulnerability_to_buildup: Vulnerabilidade ao jogo de construção.
        explanation: Explicação da análise.
        confidence: Confiança da análise (0.0 a 1.0).
    """
    intensity: str = "unknown"
    trigger_zones: List[str] = field(default_factory=list)
    defensive_line: str = "unknown"
    compactness: str = "unknown"
    recovery_speed: str = "unknown"
    vulnerability_to_buildup: str = ""
    explanation: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intensity": self.intensity,
            "trigger_zones": self.trigger_zones,
            "defensive_line": self.defensive_line,
            "compactness": self.compactness,
            "recovery_speed": self.recovery_speed,
            "vulnerability_to_buildup": self.vulnerability_to_buildup,
            "explanation": self.explanation,
            "confidence": self.confidence,
        }


# ---------------------------------------------------------------------------
# Resultado: ZoneVulnerability
# ---------------------------------------------------------------------------

@dataclass
class ZoneVulnerability:
    """
    Vulnerabilidade em uma zona específica do campo adversário.

    Campos:
        zone: Identificador da zona (ex: "left_channel", "right_halfspace").
        corridor: Corredor ("left" | "center" | "right").
        severity: Severidade ("critical" | "high" | "moderate" | "low").
        description: Descrição da vulnerabilidade.
        exploitation_method: Como explorar a vulnerabilidade.
        evidence: Evidências observadas (partidas, padrões).
        confidence: Confiança da análise (0.0 a 1.0).
    """
    zone: str = "unknown"
    corridor: str = "unknown"
    severity: str = "moderate"
    description: str = ""
    exploitation_method: str = ""
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone": self.zone,
            "corridor": self.corridor,
            "severity": self.severity,
            "description": self.description,
            "exploitation_method": self.exploitation_method,
            "evidence": self.evidence,
            "confidence": self.confidence,
        }


# ---------------------------------------------------------------------------
# Resultado: TransitionVulnerability
# ---------------------------------------------------------------------------

@dataclass
class TransitionVulnerability:
    """
    Vulnerabilidade em transição (defensiva ou ofensiva) do adversário.

    Campos:
        type: Tipo ("defensive_transition" | "offensive_transition").
        description: Descrição da vulnerabilidade.
        trigger: O que desencadeia a vulnerabilidade.
        exploitation_window: Janela de tempo para explorar (ex: "primeiros 3s").
        key_players_involved: Jogadores-chave envolvidos.
        severity: Severidade ("critical" | "high" | "moderate" | "low").
        confidence: Confiança da análise (0.0 a 1.0).
    """
    type: str = "defensive_transition"
    description: str = ""
    trigger: str = ""
    exploitation_window: str = ""
    key_players_involved: List[str] = field(default_factory=list)
    severity: str = "moderate"
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "description": self.description,
            "trigger": self.trigger,
            "exploitation_window": self.exploitation_window,
            "key_players_involved": self.key_players_involved,
            "severity": self.severity,
            "confidence": self.confidence,
        }


# ---------------------------------------------------------------------------
# Resultado: SetPieceAnalysis
# ---------------------------------------------------------------------------

@dataclass
class SetPieceAnalysis:
    """
    Análise de bola parada do adversário.

    Campos:
        offensive_threats: Ameaças ofensivas de bola parada.
        defensive_weaknesses: Fraquezas defensivas em bola parada.
        key_takers_assessment: Avaliação dos cobradores principais.
        key_targets_assessment: Avaliação dos alvos principais.
        recommended_defensive_setup: Configuração defensiva recomendada.
        recommended_offensive_approach: Abordagem ofensiva recomendada.
        confidence: Confiança da análise (0.0 a 1.0).
    """
    offensive_threats: List[str] = field(default_factory=list)
    defensive_weaknesses: List[str] = field(default_factory=list)
    key_takers_assessment: str = ""
    key_targets_assessment: str = ""
    recommended_defensive_setup: str = ""
    recommended_offensive_approach: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "offensive_threats": self.offensive_threats,
            "defensive_weaknesses": self.defensive_weaknesses,
            "key_takers_assessment": self.key_takers_assessment,
            "key_targets_assessment": self.key_targets_assessment,
            "recommended_defensive_setup": self.recommended_defensive_setup,
            "recommended_offensive_approach": self.recommended_offensive_approach,
            "confidence": self.confidence,
        }


# ---------------------------------------------------------------------------
# Resultado: TacticalAlert
# ---------------------------------------------------------------------------

@dataclass
class TacticalAlert:
    """
    Alerta tático de alta prioridade sobre o adversário.

    Campos:
        alert_id: Identificador único do alerta.
        category: Categoria ("pressing" | "transition" | "set_piece" | "zone" | "general").
        severity: Severidade ("critical" | "high" | "moderate").
        title: Título curto do alerta.
        description: Descrição detalhada.
        action_required: Ação recomendada para endereçar o alerta.
    """
    alert_id: str = "alert-unknown"
    category: str = "general"
    severity: str = "moderate"
    title: str = ""
    description: str = ""
    action_required: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "action_required": self.action_required,
        }


# ---------------------------------------------------------------------------
# Resultado: OpponentAnalysisReport
# ---------------------------------------------------------------------------

@dataclass
class OpponentAnalysisReport:
    """
    Relatório completo de análise de adversário.

    Campos:
        opponent_id: ID do adversário analisado.
        opponent_name: Nome do adversário.
        analysis_date: Data da análise.
        pressing_analysis: Análise do pressing.
        zone_vulnerabilities: Vulnerabilidades por zona.
        transition_vulnerabilities: Vulnerabilidades em transição.
        set_piece_analysis: Análise de bola parada.
        tactical_alerts: Alertas táticos de alta prioridade.
        formation_summary: Resumo das formações observadas.
        overall_threat_level: Nível de ameaça geral.
        overall_assessment: Avaliação geral em texto.
        key_observations: Observações-chave (máx 5).
        data_completeness: Completude dos dados (0.0 a 1.0).
        source_matches_count: Número de partidas usadas na análise.
    """
    opponent_id: str = "unknown"
    opponent_name: str = "Adversário Desconhecido"
    analysis_date: str = field(
        default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d")
    )
    pressing_analysis: PressingAnalysis = field(default_factory=PressingAnalysis)
    zone_vulnerabilities: List[ZoneVulnerability] = field(default_factory=list)
    transition_vulnerabilities: List[TransitionVulnerability] = field(default_factory=list)
    set_piece_analysis: SetPieceAnalysis = field(default_factory=SetPieceAnalysis)
    tactical_alerts: List[TacticalAlert] = field(default_factory=list)
    formation_summary: str = "Formação não identificada"
    overall_threat_level: str = "unknown"
    overall_assessment: str = ""
    key_observations: List[str] = field(default_factory=list)
    data_completeness: float = 0.0
    source_matches_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "opponent_id": self.opponent_id,
            "opponent_name": self.opponent_name,
            "analysis_date": self.analysis_date,
            "pressing_analysis": self.pressing_analysis.to_dict(),
            "zone_vulnerabilities": [z.to_dict() for z in self.zone_vulnerabilities],
            "transition_vulnerabilities": [t.to_dict() for t in self.transition_vulnerabilities],
            "set_piece_analysis": self.set_piece_analysis.to_dict(),
            "tactical_alerts": [a.to_dict() for a in self.tactical_alerts],
            "formation_summary": self.formation_summary,
            "overall_threat_level": self.overall_threat_level,
            "overall_assessment": self.overall_assessment,
            "key_observations": self.key_observations,
            "data_completeness": self.data_completeness,
            "source_matches_count": self.source_matches_count,
        }


# ---------------------------------------------------------------------------
# OpponentAnalyzer
# ---------------------------------------------------------------------------

class OpponentAnalyzer:
    """
    Analisador de adversários.

    Recebe um OpponentProfile (dados brutos) e produz um OpponentAnalysisReport
    com análises estruturadas, separando fato, inferência e recomendação.

    Não inventa dados: campos ausentes resultam em análises com confiança baixa
    e explicações explícitas sobre a ausência de informação.
    """

    # Mapeamento de intensidade de pressing → análise
    _PRESSING_ANALYSIS_MAP = {
        "high": {
            "compactness": "alto",
            "recovery_speed": "rápida",
            "vulnerability_to_buildup": (
                "Pressing alto cria espaços nas costas da linha defensiva. "
                "Bolas longas e passes em profundidade podem ser eficazes."
            ),
            "explanation": (
                "O adversário aplica pressing intenso no campo adversário. "
                "Gatilhos de pressing incluem o goleiro e zagueiros com bola. "
                "A linha defensiva alta cria vulnerabilidade ao contra-ataque."
            ),
        },
        "medium": {
            "compactness": "médio",
            "recovery_speed": "moderada",
            "vulnerability_to_buildup": (
                "Pressing médio permite construção com paciência. "
                "Triangulações no meio-campo podem criar superioridade numérica."
            ),
            "explanation": (
                "O adversário alterna entre pressing e bloco médio. "
                "Pressiona em zonas específicas, especialmente no corredor central. "
                "Construção com paciência pode criar desequilíbrios."
            ),
        },
        "low": {
            "compactness": "baixo",
            "recovery_speed": "lenta",
            "vulnerability_to_buildup": (
                "Pressing baixo permite construção livre. "
                "O adversário se organiza em bloco baixo e espera o erro."
            ),
            "explanation": (
                "O adversário recua em bloco baixo e espera o erro adversário. "
                "Pouco pressing no campo ofensivo. "
                "Necessário criar superioridade posicional para abrir espaços."
            ),
        },
    }

    # Mapeamento de linha defensiva → trigger zones
    _DEFENSIVE_LINE_TRIGGER_MAP = {
        "high": ["defensive_third", "middle_third"],
        "medium": ["middle_third"],
        "low": ["defensive_third"],
    }

    def analyze(
        self,
        profile: OpponentProfile,
        opponent_name: str = "Adversário",
    ) -> OpponentAnalysisReport:
        """
        Analisa um OpponentProfile e retorna um OpponentAnalysisReport.

        Args:
            profile: Perfil do adversário com dados brutos.
            opponent_name: Nome do adversário para exibição.

        Returns:
            OpponentAnalysisReport com análises estruturadas.
        """
        pressing = self._analyze_pressing(profile)
        zone_vulns = self._analyze_zone_vulnerabilities(profile)
        transition_vulns = self._analyze_transition_vulnerabilities(profile)
        set_piece = self._analyze_set_pieces(profile)
        alerts = self._generate_alerts(pressing, zone_vulns, transition_vulns, set_piece)
        formation_summary = self._summarize_formations(profile)
        threat_level = self._assess_threat_level(pressing, zone_vulns, transition_vulns)
        key_obs = self._extract_key_observations(profile, pressing, zone_vulns)
        completeness = self._calculate_completeness(profile)
        assessment = self._build_overall_assessment(
            threat_level, pressing, zone_vulns, transition_vulns, completeness
        )

        return OpponentAnalysisReport(
            opponent_id=profile.opponent_id,
            opponent_name=opponent_name,
            pressing_analysis=pressing,
            zone_vulnerabilities=zone_vulns,
            transition_vulnerabilities=transition_vulns,
            set_piece_analysis=set_piece,
            tactical_alerts=alerts,
            formation_summary=formation_summary,
            overall_threat_level=threat_level,
            overall_assessment=assessment,
            key_observations=key_obs,
            data_completeness=completeness,
            source_matches_count=len(profile.source_matches),
        )

    # ------------------------------------------------------------------
    # Pressing Analysis
    # ------------------------------------------------------------------

    def _analyze_pressing(self, profile: OpponentProfile) -> PressingAnalysis:
        """Analisa o sistema de pressing do adversário."""
        pressing_str = profile.pressing_profile.lower() if profile.pressing_profile else "unknown"

        # Extrair intensidade do texto do pressing_profile
        intensity = "unknown"
        for level in ("high", "medium", "low"):
            if level in pressing_str:
                intensity = level
                break

        # Extrair linha defensiva
        defensive_line = "unknown"
        for level in ("high", "medium", "low"):
            if level in pressing_str:
                defensive_line = level
                break

        # Buscar mapeamento de análise
        analysis_data = self._PRESSING_ANALYSIS_MAP.get(intensity, {})
        trigger_zones = self._DEFENSIVE_LINE_TRIGGER_MAP.get(defensive_line, [])

        # Confiança baseada na qualidade dos dados
        confidence = 0.0
        if profile.pressing_profile and profile.pressing_profile != "unknown":
            confidence += 0.4
        if profile.source_matches:
            confidence += min(0.4, len(profile.source_matches) * 0.1)
        if profile.formation_patterns:
            confidence += 0.2

        return PressingAnalysis(
            intensity=intensity,
            trigger_zones=trigger_zones,
            defensive_line=defensive_line,
            compactness=analysis_data.get("compactness", "desconhecida"),
            recovery_speed=analysis_data.get("recovery_speed", "desconhecida"),
            vulnerability_to_buildup=analysis_data.get("vulnerability_to_buildup", ""),
            explanation=analysis_data.get(
                "explanation",
                "Dados insuficientes para análise de pressing. "
                "Recomenda-se análise de vídeo de pelo menos 3 partidas recentes.",
            ),
            confidence=round(min(confidence, 1.0), 2),
        )

    # ------------------------------------------------------------------
    # Zone Vulnerabilities
    # ------------------------------------------------------------------

    def _analyze_zone_vulnerabilities(
        self, profile: OpponentProfile
    ) -> List[ZoneVulnerability]:
        """Analisa vulnerabilidades por zona a partir dos weak_zones do perfil."""
        if not profile.weak_zones:
            return []

        vulnerabilities = []
        for i, zone_desc in enumerate(profile.weak_zones):
            zone_lower = zone_desc.lower()

            # Detectar corredor
            if any(w in zone_lower for w in ("left", "esquerda", "esq")):
                corridor = "left"
            elif any(w in zone_lower for w in ("right", "direita", "dir")):
                corridor = "right"
            elif any(w in zone_lower for w in ("center", "central", "meio")):
                corridor = "center"
            else:
                corridor = "unknown"

            # Detectar severidade
            if any(w in zone_lower for w in ("crítica", "critical", "grave")):
                severity = "critical"
            elif any(w in zone_lower for w in ("alta", "high", "importante")):
                severity = "high"
            elif any(w in zone_lower for w in ("baixa", "low", "menor")):
                severity = "low"
            else:
                severity = "moderate"

            # Método de exploração baseado no corredor
            exploitation_map = {
                "left": "Atacar pelo corredor esquerdo com sobreposição do lateral.",
                "right": "Atacar pelo corredor direito com sobreposição do lateral.",
                "center": "Explorar o espaço entre linhas com o meia criativo.",
                "unknown": "Identificar padrão específico via análise de vídeo.",
            }

            confidence = 0.5
            if profile.source_matches:
                confidence += min(0.3, len(profile.source_matches) * 0.1)

            vulnerabilities.append(
                ZoneVulnerability(
                    zone=f"zone_{i + 1}",
                    corridor=corridor,
                    severity=severity,
                    description=zone_desc,
                    exploitation_method=exploitation_map.get(corridor, ""),
                    evidence=profile.source_matches[:3],
                    confidence=round(min(confidence, 1.0), 2),
                )
            )

        return vulnerabilities

    # ------------------------------------------------------------------
    # Transition Vulnerabilities
    # ------------------------------------------------------------------

    def _analyze_transition_vulnerabilities(
        self, profile: OpponentProfile
    ) -> List[TransitionVulnerability]:
        """Analisa vulnerabilidades em transição."""
        if not profile.transition_vulnerabilities:
            return []

        result = []
        for i, vuln_desc in enumerate(profile.transition_vulnerabilities):
            vuln_lower = vuln_desc.lower()

            # Detectar tipo de transição
            if any(w in vuln_lower for w in ("defensiva", "defensive", "perda", "loss")):
                t_type = "defensive_transition"
                trigger = "Perda de bola no campo ofensivo."
                window = "Primeiros 3 segundos após a perda."
            else:
                t_type = "offensive_transition"
                trigger = "Recuperação de bola no campo defensivo."
                window = "Primeiros 5 segundos após a recuperação."

            # Detectar severidade
            if any(w in vuln_lower for w in ("crítica", "critical", "grave", "alta")):
                severity = "high"
            else:
                severity = "moderate"

            confidence = 0.5
            if profile.source_matches:
                confidence += min(0.3, len(profile.source_matches) * 0.1)

            result.append(
                TransitionVulnerability(
                    type=t_type,
                    description=vuln_desc,
                    trigger=trigger,
                    exploitation_window=window,
                    key_players_involved=[],
                    severity=severity,
                    confidence=round(min(confidence, 1.0), 2),
                )
            )

        return result

    # ------------------------------------------------------------------
    # Set Piece Analysis
    # ------------------------------------------------------------------

    def _analyze_set_pieces(self, profile: OpponentProfile) -> SetPieceAnalysis:
        """Analisa o perfil de bola parada do adversário."""
        sp = profile.set_piece_profile
        confidence = 0.0

        offensive_threats = []
        defensive_weaknesses = []

        # Análise de escanteios
        if sp.corners_routine and sp.corners_routine != "unknown":
            confidence += 0.2
            offensive_threats.append(
                f"Escanteios: {sp.corners_routine}"
            )

        # Análise de faltas
        if sp.free_kick_routine and sp.free_kick_routine != "unknown":
            confidence += 0.2
            offensive_threats.append(
                f"Faltas: {sp.free_kick_routine}"
            )

        # Análise defensiva
        if sp.defensive_set_piece and sp.defensive_set_piece != "unknown":
            confidence += 0.2
            if any(w in sp.defensive_set_piece.lower() for w in ("fraco", "weak", "vulnerável")):
                defensive_weaknesses.append(sp.defensive_set_piece)

        # Cobradores
        takers_assessment = ""
        if sp.key_takers:
            confidence += 0.2
            takers_assessment = (
                f"Cobradores identificados: {', '.join(sp.key_takers)}. "
                "Atenção especial na marcação desses jogadores."
            )

        # Alvos
        targets_assessment = ""
        if sp.key_targets:
            confidence += 0.2
            targets_assessment = (
                f"Alvos principais: {', '.join(sp.key_targets)}. "
                "Marcar individualmente esses jogadores em bolas paradas."
            )

        # Recomendações
        def_setup = (
            "Marcar individualmente os alvos principais. "
            "Posicionar jogadores de altura nas zonas de escanteio."
            if sp.key_targets else
            "Dados insuficientes. Analisar vídeo de bola parada defensiva."
        )
        off_approach = (
            "Explorar a defesa de bola parada adversária com variações de rotina."
            if not defensive_weaknesses else
            f"Explorar fraqueza identificada: {defensive_weaknesses[0]}"
        )

        if not sp.key_takers and not sp.key_targets and sp.corners_routine == "unknown":
            confidence = 0.1

        return SetPieceAnalysis(
            offensive_threats=offensive_threats,
            defensive_weaknesses=defensive_weaknesses,
            key_takers_assessment=takers_assessment,
            key_targets_assessment=targets_assessment,
            recommended_defensive_setup=def_setup,
            recommended_offensive_approach=off_approach,
            confidence=round(min(confidence, 1.0), 2),
        )

    # ------------------------------------------------------------------
    # Tactical Alerts
    # ------------------------------------------------------------------

    def _generate_alerts(
        self,
        pressing: PressingAnalysis,
        zone_vulns: List[ZoneVulnerability],
        transition_vulns: List[TransitionVulnerability],
        set_piece: SetPieceAnalysis,
    ) -> List[TacticalAlert]:
        """Gera alertas táticos de alta prioridade."""
        alerts = []
        alert_counter = 1

        # Alerta de pressing alto
        if pressing.intensity == "high":
            alerts.append(
                TacticalAlert(
                    alert_id=f"alert-{alert_counter:03d}",
                    category="pressing",
                    severity="high",
                    title="Pressing de Alta Intensidade",
                    description=(
                        "O adversário aplica pressing intenso. "
                        "A construção desde o goleiro será pressionada."
                    ),
                    action_required=(
                        "Treinar saída de bola sob pressão. "
                        "Preparar opção de bola longa para o segundo tempo."
                    ),
                )
            )
            alert_counter += 1

        # Alertas de zonas críticas
        critical_zones = [z for z in zone_vulns if z.severity == "critical"]
        if critical_zones:
            for zone in critical_zones:
                alerts.append(
                    TacticalAlert(
                        alert_id=f"alert-{alert_counter:03d}",
                        category="zone",
                        severity="critical",
                        title=f"Vulnerabilidade Crítica — Corredor {zone.corridor.title()}",
                        description=zone.description,
                        action_required=zone.exploitation_method,
                    )
                )
                alert_counter += 1

        # Alertas de transição crítica
        critical_transitions = [t for t in transition_vulns if t.severity == "high"]
        if critical_transitions:
            for trans in critical_transitions:
                alerts.append(
                    TacticalAlert(
                        alert_id=f"alert-{alert_counter:03d}",
                        category="transition",
                        severity="high",
                        title=f"Vulnerabilidade em Transição — {trans.type.replace('_', ' ').title()}",
                        description=trans.description,
                        action_required=(
                            f"Explorar na janela: {trans.exploitation_window}"
                        ),
                    )
                )
                alert_counter += 1

        # Alerta de bola parada com cobradores identificados
        if set_piece.key_takers_assessment:
            alerts.append(
                TacticalAlert(
                    alert_id=f"alert-{alert_counter:03d}",
                    category="set_piece",
                    severity="moderate",
                    title="Cobradores de Bola Parada Identificados",
                    description=set_piece.key_takers_assessment,
                    action_required=(
                        "Marcar individualmente os cobradores. "
                        "Revisar posicionamento defensivo em bola parada."
                    ),
                )
            )
            alert_counter += 1

        return alerts

    # ------------------------------------------------------------------
    # Formation Summary
    # ------------------------------------------------------------------

    def _summarize_formations(self, profile: OpponentProfile) -> str:
        """Resume as formações observadas do adversário."""
        if not profile.formation_patterns:
            return "Formação não identificada. Dados insuficientes."

        if len(profile.formation_patterns) == 1:
            return f"Formação principal: {profile.formation_patterns[0]}."

        primary = profile.formation_patterns[0]
        alternates = ", ".join(profile.formation_patterns[1:])
        return (
            f"Formação principal: {primary}. "
            f"Variações observadas: {alternates}."
        )

    # ------------------------------------------------------------------
    # Threat Level
    # ------------------------------------------------------------------

    def _assess_threat_level(
        self,
        pressing: PressingAnalysis,
        zone_vulns: List[ZoneVulnerability],
        transition_vulns: List[TransitionVulnerability],
    ) -> str:
        """Avalia o nível de ameaça geral do adversário."""
        score = 0

        # Pressing
        if pressing.intensity == "high":
            score += 3
        elif pressing.intensity == "medium":
            score += 2
        elif pressing.intensity == "low":
            score += 1

        # Zonas críticas (adversário sem vulnerabilidades = mais perigoso)
        critical_zones = sum(1 for z in zone_vulns if z.severity == "critical")
        high_zones = sum(1 for z in zone_vulns if z.severity == "high")
        if critical_zones == 0 and high_zones == 0:
            score += 2  # Poucos pontos fracos = mais perigoso
        elif critical_zones > 0:
            score -= 1  # Muitos pontos fracos = menos perigoso

        # Transições
        high_transitions = sum(1 for t in transition_vulns if t.severity == "high")
        if high_transitions == 0:
            score += 1

        if score >= 5:
            return "critical"
        elif score >= 4:
            return "high"
        elif score >= 2:
            return "moderate"
        else:
            return "low"

    # ------------------------------------------------------------------
    # Key Observations
    # ------------------------------------------------------------------

    def _extract_key_observations(
        self,
        profile: OpponentProfile,
        pressing: PressingAnalysis,
        zone_vulns: List[ZoneVulnerability],
    ) -> List[str]:
        """Extrai as observações-chave mais relevantes (máx 5)."""
        observations = []

        if pressing.intensity != "unknown":
            observations.append(
                f"Pressing de intensidade {pressing.intensity}: {pressing.explanation[:80]}..."
                if len(pressing.explanation) > 80
                else f"Pressing de intensidade {pressing.intensity}: {pressing.explanation}"
            )

        if profile.formation_patterns:
            observations.append(
                f"Formação principal: {profile.formation_patterns[0]}."
            )

        for zone in zone_vulns[:2]:
            observations.append(
                f"Vulnerabilidade no corredor {zone.corridor}: {zone.description}"
            )

        if profile.set_piece_profile.key_takers:
            observations.append(
                f"Cobradores de bola parada: {', '.join(profile.set_piece_profile.key_takers)}."
            )

        return observations[:5]

    # ------------------------------------------------------------------
    # Data Completeness
    # ------------------------------------------------------------------

    def _calculate_completeness(self, profile: OpponentProfile) -> float:
        """Calcula a completude dos dados do perfil (0.0 a 1.0)."""
        total_fields = 6
        filled = 0

        if profile.formation_patterns:
            filled += 1
        if profile.pressing_profile and profile.pressing_profile != "unknown":
            filled += 1
        if profile.weak_zones:
            filled += 1
        if profile.transition_vulnerabilities:
            filled += 1
        sp = profile.set_piece_profile
        if sp.corners_routine != "unknown" or sp.free_kick_routine != "unknown":
            filled += 1
        if profile.source_matches:
            filled += 1

        return round(filled / total_fields, 2)

    # ------------------------------------------------------------------
    # Overall Assessment
    # ------------------------------------------------------------------

    def _build_overall_assessment(
        self,
        threat_level: str,
        pressing: PressingAnalysis,
        zone_vulns: List[ZoneVulnerability],
        transition_vulns: List[TransitionVulnerability],
        completeness: float,
    ) -> str:
        """Constrói a avaliação geral em texto."""
        threat_labels = {
            "critical": "adversário de alto risco",
            "high": "adversário perigoso",
            "moderate": "adversário de nível médio",
            "low": "adversário com vulnerabilidades exploráveis",
            "unknown": "adversário com dados insuficientes para avaliação",
        }
        label = threat_labels.get(threat_level, "adversário")

        parts = [f"Análise indica {label}."]

        if pressing.intensity != "unknown":
            parts.append(
                f"Pressing de intensidade {pressing.intensity} "
                f"com linha defensiva {pressing.defensive_line}."
            )

        critical_zones = [z for z in zone_vulns if z.severity in ("critical", "high")]
        if critical_zones:
            corridors = list({z.corridor for z in critical_zones})
            parts.append(
                f"Vulnerabilidades identificadas nos corredores: {', '.join(corridors)}."
            )
        elif zone_vulns:
            parts.append("Vulnerabilidades moderadas identificadas em zonas específicas.")
        else:
            parts.append("Nenhuma vulnerabilidade de zona identificada nos dados disponíveis.")

        if transition_vulns:
            parts.append(
                f"{len(transition_vulns)} vulnerabilidade(s) em transição identificada(s)."
            )

        if completeness < 0.4:
            parts.append(
                f"Atenção: completude dos dados é {completeness:.0%}. "
                "Recomenda-se análise de vídeo adicional antes do jogo."
            )

        return " ".join(parts)
