"""
squad_analyzer.py — Análise de Elenco para o SPFC Champion Decision OS.

Módulo de Squad Intelligence: analisa profundidade por posição, lacunas de
papéis táticos, dependências de jogadores e curva etária.

Princípios:
- Não inventar dados — análise baseada apenas nos dados fornecidos.
- Separar fato (dados do elenco) de inferência (análise de lacunas).
- Explicabilidade obrigatória — toda lacuna identificada tem justificativa.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.core.football_models import (
    AvailabilityStatus,
    Player,
    PositionDepth,
    SquadProfile,
)


# ---------------------------------------------------------------------------
# Definição de Papéis Táticos
# ---------------------------------------------------------------------------

@dataclass
class RoleDefinition:
    """
    Definição de um papel tático no modelo de jogo.

    Campos:
        role_id: Identificador único do papel.
        name: Nome do papel.
        positions: Posições compatíveis com este papel.
        description: Descrição das responsabilidades.
        key_attributes: Atributos principais necessários.
        minimum_squad_count: Mínimo de jogadores para este papel no elenco.
    """
    role_id: str = "unknown"
    name: str = "Unknown Role"
    positions: List[str] = field(default_factory=list)
    description: str = ""
    key_attributes: List[str] = field(default_factory=list)
    minimum_squad_count: int = 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role_id": self.role_id,
            "name": self.name,
            "positions": self.positions,
            "description": self.description,
            "key_attributes": self.key_attributes,
            "minimum_squad_count": self.minimum_squad_count,
        }


# Papéis táticos de referência para o modelo 4-3-3 do SPFC
SPFC_REFERENCE_ROLES: List[RoleDefinition] = [
    RoleDefinition(
        role_id="gk",
        name="Goleiro",
        positions=["GK"],
        description="Goleiro titular e reserva.",
        key_attributes=["reflexos", "saída de bola", "comunicação"],
        minimum_squad_count=2,
    ),
    RoleDefinition(
        role_id="ball_playing_cb",
        name="Zagueiro Construtor",
        positions=["CB"],
        description="Zagueiro com capacidade de iniciar jogadas e sair jogando.",
        key_attributes=["passe longo", "visão de jogo", "liderança defensiva"],
        minimum_squad_count=2,
    ),
    RoleDefinition(
        role_id="stopper_cb",
        name="Zagueiro Marcador",
        positions=["CB"],
        description="Zagueiro com perfil mais marcador e agressivo.",
        key_attributes=["duelos aéreos", "marcação individual", "força física"],
        minimum_squad_count=1,
    ),
    RoleDefinition(
        role_id="attacking_lb",
        name="Lateral Esquerdo Ofensivo",
        positions=["LB"],
        description="Lateral esquerdo com capacidade de sobreposição e cruzamento.",
        key_attributes=["cruzamento", "sobreposição", "resistência"],
        minimum_squad_count=2,
    ),
    RoleDefinition(
        role_id="attacking_rb",
        name="Lateral Direito Ofensivo",
        positions=["RB"],
        description="Lateral direito com capacidade de sobreposição e cruzamento.",
        key_attributes=["cruzamento", "sobreposição", "resistência"],
        minimum_squad_count=2,
    ),
    RoleDefinition(
        role_id="defensive_mid",
        name="Volante Destruidor",
        positions=["DM", "CM"],
        description="Volante com perfil defensivo, recuperação de bola e proteção da defesa.",
        key_attributes=["interceptação", "duelos", "posicionamento defensivo"],
        minimum_squad_count=2,
    ),
    RoleDefinition(
        role_id="box_to_box_mid",
        name="Meia Box-to-Box",
        positions=["CM", "DM"],
        description="Meia com capacidade de cobrir todo o campo, atacar e defender.",
        key_attributes=["resistência", "finalização de média distância", "passes"],
        minimum_squad_count=2,
    ),
    RoleDefinition(
        role_id="creative_mid",
        name="Meia Criativo",
        positions=["CM", "AM"],
        description="Meia com perfil criativo, responsável pela criação de chances.",
        key_attributes=["visão de jogo", "drible", "passe decisivo"],
        minimum_squad_count=1,
    ),
    RoleDefinition(
        role_id="winger_right",
        name="Extremo Direito",
        positions=["RW", "RM"],
        description="Extremo direito com velocidade e capacidade de driblar.",
        key_attributes=["velocidade", "drible", "finalização"],
        minimum_squad_count=2,
    ),
    RoleDefinition(
        role_id="winger_left",
        name="Extremo Esquerdo",
        positions=["LW", "LM"],
        description="Extremo esquerdo com velocidade e capacidade de driblar.",
        key_attributes=["velocidade", "drible", "finalização"],
        minimum_squad_count=2,
    ),
    RoleDefinition(
        role_id="striker",
        name="Centroavante",
        positions=["ST", "CF"],
        description="Centroavante referência, finalizador e ponto de apoio.",
        key_attributes=["finalização", "jogo aéreo", "hold-up play"],
        minimum_squad_count=2,
    ),
]

ROLE_MAP: Dict[str, RoleDefinition] = {r.role_id: r for r in SPFC_REFERENCE_ROLES}


# ---------------------------------------------------------------------------
# Análise de Elenco
# ---------------------------------------------------------------------------

@dataclass
class GapAnalysis:
    """
    Resultado da análise de lacunas do elenco.

    Campos:
        role_id: ID do papel com lacuna.
        role_name: Nome do papel.
        current_count: Quantidade atual de jogadores para este papel.
        minimum_required: Mínimo necessário.
        available_count: Jogadores disponíveis (excluindo lesionados/suspensos).
        gap_severity: Severidade da lacuna ("critical", "moderate", "minor", "none").
        explanation: Explicação da lacuna.
        suggested_action: Ação sugerida para cobrir a lacuna.
    """
    role_id: str = "unknown"
    role_name: str = "unknown"
    current_count: int = 0
    minimum_required: int = 2
    available_count: int = 0
    gap_severity: str = "none"
    explanation: str = ""
    suggested_action: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role_id": self.role_id,
            "role_name": self.role_name,
            "current_count": self.current_count,
            "minimum_required": self.minimum_required,
            "available_count": self.available_count,
            "gap_severity": self.gap_severity,
            "explanation": self.explanation,
            "suggested_action": self.suggested_action,
        }


@dataclass
class AgeCurveAnalysis:
    """Análise da curva etária do elenco."""
    u23_count: int = 0
    prime_count: int = 0       # 23–29 anos
    experienced_count: int = 0  # 30+ anos
    unknown_age_count: int = 0
    average_age: Optional[float] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "u23_count": self.u23_count,
            "prime_count": self.prime_count,
            "experienced_count": self.experienced_count,
            "unknown_age_count": self.unknown_age_count,
            "average_age": self.average_age,
            "notes": self.notes,
        }


@dataclass
class SquadAnalysisReport:
    """
    Relatório completo de análise do elenco.

    Campos:
        team_id: ID da equipe.
        season: Temporada analisada.
        total_players: Total de jogadores no elenco.
        available_players: Jogadores disponíveis.
        unavailable_players: Jogadores indisponíveis (lesionados, suspensos).
        depth_by_position: Profundidade por posição.
        gap_analysis: Análise de lacunas por papel tático.
        age_curve: Análise da curva etária.
        key_dependencies: Jogadores com alta dependência (sem reserva adequada).
        overall_assessment: Avaliação geral do elenco.
        recommendations: Recomendações baseadas na análise.
        data_completeness: Completude dos dados (0.0 a 1.0).
        notes: Observações do analista.
    """
    team_id: str = "unknown"
    season: str = "unknown"
    total_players: int = 0
    available_players: int = 0
    unavailable_players: int = 0
    depth_by_position: List[PositionDepth] = field(default_factory=list)
    gap_analysis: List[GapAnalysis] = field(default_factory=list)
    age_curve: AgeCurveAnalysis = field(default_factory=AgeCurveAnalysis)
    key_dependencies: List[str] = field(default_factory=list)
    overall_assessment: str = ""
    recommendations: List[str] = field(default_factory=list)
    data_completeness: float = 0.0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "team_id": self.team_id,
            "season": self.season,
            "total_players": self.total_players,
            "available_players": self.available_players,
            "unavailable_players": self.unavailable_players,
            "depth_by_position": [d.to_dict() for d in self.depth_by_position],
            "gap_analysis": [g.to_dict() for g in self.gap_analysis],
            "age_curve": self.age_curve.to_dict(),
            "key_dependencies": self.key_dependencies,
            "overall_assessment": self.overall_assessment,
            "recommendations": self.recommendations,
            "data_completeness": self.data_completeness,
            "notes": self.notes,
        }


class SquadAnalyzer:
    """
    Analisador de elenco do SPFC Champion Decision OS.

    Recebe uma lista de jogadores e produz um relatório de análise
    de profundidade, lacunas e curva etária.

    Princípio: Não inventar dados — análise baseada apenas nos dados fornecidos.
    """

    UNAVAILABLE_STATUSES = {
        AvailabilityStatus.INJURED,
        AvailabilityStatus.SUSPENDED,
    }

    def analyze(
        self,
        players: List[Player],
        team_id: str = "unknown",
        season: str = "unknown",
        reference_roles: Optional[List[RoleDefinition]] = None,
    ) -> SquadAnalysisReport:
        """
        Analisa o elenco e retorna um relatório completo.

        Args:
            players: Lista de jogadores do elenco.
            team_id: ID da equipe.
            season: Temporada.
            reference_roles: Papéis de referência (padrão: SPFC_REFERENCE_ROLES).

        Returns:
            SquadAnalysisReport com análise completa.
        """
        roles = reference_roles or SPFC_REFERENCE_ROLES

        available = [
            p for p in players
            if p.availability_status not in self.UNAVAILABLE_STATUSES
        ]
        unavailable = [
            p for p in players
            if p.availability_status in self.UNAVAILABLE_STATUSES
        ]

        depth = self._analyze_depth(players, available)
        gaps = self._analyze_gaps(players, available, roles)
        age_curve = self._analyze_age_curve(players)
        dependencies = self._find_key_dependencies(players, available, roles)

        # Completude dos dados: proporção de jogadores com posição definida
        with_positions = sum(1 for p in players if len(p.positions) > 0)
        completeness = with_positions / len(players) if players else 0.0

        # Avaliação geral baseada nos gaps críticos
        critical_gaps = [g for g in gaps if g.gap_severity == "critical"]
        if critical_gaps:
            assessment = (
                f"Elenco com {len(critical_gaps)} lacuna(s) crítica(s) identificada(s). "
                "Ação prioritária necessária."
            )
        elif any(g.gap_severity == "moderate" for g in gaps):
            assessment = (
                "Elenco com lacunas moderadas. "
                "Monitoramento e planejamento de reforços recomendado."
            )
        else:
            assessment = "Elenco com cobertura adequada para os papéis analisados."

        # Recomendações baseadas nos gaps (inferência, não fato)
        recommendations = []
        for gap in gaps:
            if gap.gap_severity in ("critical", "moderate"):
                recommendations.append(gap.suggested_action)

        return SquadAnalysisReport(
            team_id=team_id,
            season=season,
            total_players=len(players),
            available_players=len(available),
            unavailable_players=len(unavailable),
            depth_by_position=depth,
            gap_analysis=gaps,
            age_curve=age_curve,
            key_dependencies=dependencies,
            overall_assessment=assessment,
            recommendations=recommendations,
            data_completeness=round(completeness, 2),
            notes=(
                "Análise baseada nos dados fornecidos. "
                "Completude dos dados: "
                f"{round(completeness * 100)}%. "
                "Dados incompletos podem subestimar lacunas."
            ),
        )

    def _analyze_depth(
        self,
        all_players: List[Player],
        available_players: List[Player],
    ) -> List[PositionDepth]:
        """Analisa profundidade por posição."""
        position_map: Dict[str, List[str]] = {}
        available_ids = {p.player_id for p in available_players}

        for player in all_players:
            for pos in player.positions:
                if pos not in position_map:
                    position_map[pos] = []
                position_map[pos].append(player.player_id)

        result = []
        for pos, player_ids in sorted(position_map.items()):
            available_in_pos = [pid for pid in player_ids if pid in available_ids]
            has_gap = len(available_in_pos) < 2
            result.append(
                PositionDepth(
                    position=pos,
                    players=player_ids,
                    depth_count=len(available_in_pos),
                    has_gap=has_gap,
                    gap_reason=(
                        f"Apenas {len(available_in_pos)} jogador(es) disponível(is) "
                        f"para a posição {pos}."
                        if has_gap else ""
                    ),
                )
            )
        return result

    def _analyze_gaps(
        self,
        all_players: List[Player],
        available_players: List[Player],
        roles: List[RoleDefinition],
    ) -> List[GapAnalysis]:
        """Analisa lacunas por papel tático."""
        available_ids = {p.player_id for p in available_players}
        gaps = []

        for role in roles:
            # Jogadores que cobrem este papel (por posição)
            covering = [
                p for p in all_players
                if any(pos in role.positions for pos in p.positions)
                or role.role_id in p.roles
            ]
            available_covering = [
                p for p in covering if p.player_id in available_ids
            ]

            total = len(covering)
            avail = len(available_covering)
            minimum = role.minimum_squad_count

            if avail == 0:
                severity = "critical"
                explanation = (
                    f"Nenhum jogador disponível para o papel '{role.name}'. "
                    "Risco operacional imediato."
                )
                action = (
                    f"Prioridade máxima: identificar jogador para cobrir '{role.name}' "
                    "no mercado ou adaptar jogador de posição similar."
                )
            elif avail < minimum:
                severity = "critical" if avail == 1 and minimum >= 2 else "moderate"
                explanation = (
                    f"Apenas {avail} jogador(es) disponível(is) para '{role.name}'. "
                    f"Mínimo recomendado: {minimum}."
                )
                action = (
                    f"Reforçar '{role.name}' com pelo menos "
                    f"{minimum - avail} jogador(es) adicional(is)."
                )
            elif total < minimum:
                severity = "moderate"
                explanation = (
                    f"Total de {total} jogador(es) para '{role.name}', "
                    f"abaixo do mínimo de {minimum}. "
                    "Vulnerável a lesões."
                )
                action = (
                    f"Monitorar '{role.name}' — considerar reforço preventivo."
                )
            else:
                severity = "none"
                explanation = f"Cobertura adequada para '{role.name}'."
                action = ""

            gaps.append(
                GapAnalysis(
                    role_id=role.role_id,
                    role_name=role.name,
                    current_count=total,
                    minimum_required=minimum,
                    available_count=avail,
                    gap_severity=severity,
                    explanation=explanation,
                    suggested_action=action,
                )
            )

        return gaps

    def _analyze_age_curve(self, players: List[Player]) -> AgeCurveAnalysis:
        """Analisa a distribuição etária do elenco."""
        u23 = prime = experienced = unknown = 0
        ages = []

        for p in players:
            if p.age is None:
                unknown += 1
            elif p.age < 23:
                u23 += 1
                ages.append(p.age)
            elif p.age <= 29:
                prime += 1
                ages.append(p.age)
            else:
                experienced += 1
                ages.append(p.age)

        avg = round(sum(ages) / len(ages), 1) if ages else None

        notes = ""
        if unknown > 0:
            notes = (
                f"{unknown} jogador(es) sem idade registrada — "
                "análise etária pode estar incompleta."
            )

        return AgeCurveAnalysis(
            u23_count=u23,
            prime_count=prime,
            experienced_count=experienced,
            unknown_age_count=unknown,
            average_age=avg,
            notes=notes,
        )

    def _find_key_dependencies(
        self,
        all_players: List[Player],
        available_players: List[Player],
        roles: List[RoleDefinition],
    ) -> List[str]:
        """
        Identifica jogadores com alta dependência — papéis onde há apenas
        um jogador disponível.
        """
        available_ids = {p.player_id for p in available_players}
        dependencies = []

        for role in roles:
            covering_available = [
                p for p in available_players
                if any(pos in role.positions for pos in p.positions)
                or role.role_id in p.roles
            ]
            if len(covering_available) == 1:
                player = covering_available[0]
                dependencies.append(
                    f"{player.name} — único disponível para '{role.name}'"
                )

        return dependencies
