"""
football_models.py — Modelos de domínio do futebol para o SPFC Champion Decision OS.

Modelos: Team, Player, Match, PlayState, TacticalBranch, SquadProfile,
         OpponentProfile, ScoutingTarget, DecisionReport.

Regras (03_DATA_MODEL.md):
- Todo modelo tem validação, serialização, defaults seguros, erro claro e teste.
- Não inventar dados: nenhum campo tem valor padrão inventado.
- Separar fato, inferência e recomendação.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Foot(str, Enum):
    RIGHT = "right"
    LEFT = "left"
    BOTH = "both"
    UNKNOWN = "unknown"


class AvailabilityStatus(str, Enum):
    AVAILABLE = "available"
    INJURED = "injured"
    SUSPENDED = "suspended"
    DOUBTFUL = "doubtful"
    UNKNOWN = "unknown"


class MatchPhase(str, Enum):
    BUILDUP = "buildup"
    PROGRESSION = "progression"
    FINAL_THIRD = "final_third"
    TRANSITION_ATTACK = "transition_attack"
    TRANSITION_DEFENSE = "transition_defense"
    SET_PIECE_ATTACK = "set_piece_attack"
    SET_PIECE_DEFENSE = "set_piece_defense"
    DEFENSIVE_BLOCK = "defensive_block"
    UNKNOWN = "unknown"


class GameState(str, Enum):
    """Estado do placar no contexto da partida."""
    WINNING = "winning"
    DRAWING = "drawing"
    LOSING = "losing"
    UNKNOWN = "unknown"


class RecommendationLevel(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    NOT_RECOMMENDED = "not_recommended"


class DataSource(str, Enum):
    TRACKING = "tracking"
    VIDEO = "video"
    MANUAL = "manual"
    FIXTURE = "fixture"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Team
# ---------------------------------------------------------------------------

@dataclass
class StyleProfile:
    """
    Perfil de estilo de jogo de uma equipe.
    Todos os campos são descritivos — não inventar valores numéricos.
    """
    pressing_intensity: str = "unknown"       # "high" | "medium" | "low" | "unknown"
    defensive_line: str = "unknown"           # "high" | "medium" | "low" | "unknown"
    buildup_style: str = "unknown"            # "short" | "direct" | "mixed" | "unknown"
    width_preference: str = "unknown"         # "wide" | "central" | "mixed" | "unknown"
    transition_speed: str = "unknown"         # "fast" | "controlled" | "unknown"
    set_piece_focus: str = "unknown"          # "high" | "medium" | "low" | "unknown"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pressing_intensity": self.pressing_intensity,
            "defensive_line": self.defensive_line,
            "buildup_style": self.buildup_style,
            "width_preference": self.width_preference,
            "transition_speed": self.transition_speed,
            "set_piece_focus": self.set_piece_focus,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StyleProfile":
        return cls(
            pressing_intensity=d.get("pressing_intensity", "unknown"),
            defensive_line=d.get("defensive_line", "unknown"),
            buildup_style=d.get("buildup_style", "unknown"),
            width_preference=d.get("width_preference", "unknown"),
            transition_speed=d.get("transition_speed", "unknown"),
            set_piece_focus=d.get("set_piece_focus", "unknown"),
            notes=d.get("notes", ""),
        )


@dataclass
class Team:
    """
    Representação de uma equipe de futebol.

    Campos:
        team_id: Identificador único da equipe.
        name: Nome oficial da equipe.
        season: Temporada (ex: "2025").
        competition: Competição principal (ex: "Brasileirão Série A").
        coach: Nome do treinador.
        default_formation: Formação padrão (ex: "4-3-3").
        style_profile: Perfil de estilo de jogo.
    """
    team_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unknown Team"
    season: str = "unknown"
    competition: str = "unknown"
    coach: str = "unknown"
    default_formation: str = "unknown"
    style_profile: StyleProfile = field(default_factory=StyleProfile)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "team_id": self.team_id,
            "name": self.name,
            "season": self.season,
            "competition": self.competition,
            "coach": self.coach,
            "default_formation": self.default_formation,
            "style_profile": self.style_profile.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Team":
        return cls(
            team_id=d.get("team_id", str(uuid.uuid4())),
            name=d.get("name", "Unknown Team"),
            season=d.get("season", "unknown"),
            competition=d.get("competition", "unknown"),
            coach=d.get("coach", "unknown"),
            default_formation=d.get("default_formation", "unknown"),
            style_profile=StyleProfile.from_dict(d.get("style_profile", {})),
        )


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

@dataclass
class Player:
    """
    Representação de um jogador de futebol.

    Campos:
        player_id: Identificador único do jogador.
        name: Nome do jogador.
        age: Idade do jogador (None se desconhecida).
        preferred_foot: Pé dominante.
        positions: Lista de posições (ex: ["CB", "RB"]).
        roles: Lista de papéis táticos (ex: ["ball_playing_cb", "stopper"]).
        availability_status: Status de disponibilidade.
        nationality: Nacionalidade.
        current_club: Clube atual.
        contract_until: Data de término de contrato.
        notes: Observações livres.
    """
    player_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unknown Player"
    age: Optional[int] = None
    preferred_foot: Foot = Foot.UNKNOWN
    positions: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    availability_status: AvailabilityStatus = AvailabilityStatus.UNKNOWN
    nationality: str = "unknown"
    current_club: str = "unknown"
    contract_until: Optional[str] = None   # ISO date string "YYYY-MM-DD"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "name": self.name,
            "age": self.age,
            "preferred_foot": self.preferred_foot.value,
            "positions": self.positions,
            "roles": self.roles,
            "availability_status": self.availability_status.value,
            "nationality": self.nationality,
            "current_club": self.current_club,
            "contract_until": self.contract_until,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Player":
        foot_val = d.get("preferred_foot", "unknown")
        try:
            foot = Foot(foot_val)
        except ValueError:
            raise ValueError(
                f"preferred_foot inválido: '{foot_val}'. "
                f"Valores válidos: {[f.value for f in Foot]}"
            )

        avail_val = d.get("availability_status", "unknown")
        try:
            avail = AvailabilityStatus(avail_val)
        except ValueError:
            raise ValueError(
                f"availability_status inválido: '{avail_val}'. "
                f"Valores válidos: {[a.value for a in AvailabilityStatus]}"
            )

        return cls(
            player_id=d.get("player_id", str(uuid.uuid4())),
            name=d.get("name", "Unknown Player"),
            age=d.get("age"),
            preferred_foot=foot,
            positions=d.get("positions", []),
            roles=d.get("roles", []),
            availability_status=avail,
            nationality=d.get("nationality", "unknown"),
            current_club=d.get("current_club", "unknown"),
            contract_until=d.get("contract_until"),
            notes=d.get("notes", ""),
        )


# ---------------------------------------------------------------------------
# Match
# ---------------------------------------------------------------------------

@dataclass
class Score:
    home: int = 0
    away: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {"home": self.home, "away": self.away}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Score":
        return cls(home=int(d.get("home", 0)), away=int(d.get("away", 0)))


@dataclass
class Match:
    """
    Representação de uma partida de futebol.

    Campos:
        match_id: Identificador único da partida.
        date: Data da partida (ISO string "YYYY-MM-DD").
        home_team: Nome ou ID do time mandante.
        away_team: Nome ou ID do time visitante.
        competition: Competição.
        round: Rodada ou fase.
        score: Placar final (None se não disputada).
        venue: Local da partida.
        context: Contexto adicional (importância, pressão, etc.).
    """
    match_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    date: Optional[str] = None
    home_team: str = "unknown"
    away_team: str = "unknown"
    competition: str = "unknown"
    round: str = "unknown"
    score: Optional[Score] = None
    venue: str = "unknown"
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "match_id": self.match_id,
            "date": self.date,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "competition": self.competition,
            "round": self.round,
            "score": self.score.to_dict() if self.score else None,
            "venue": self.venue,
            "context": self.context,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Match":
        score_data = d.get("score")
        score = Score.from_dict(score_data) if score_data else None
        return cls(
            match_id=d.get("match_id", str(uuid.uuid4())),
            date=d.get("date"),
            home_team=d.get("home_team", "unknown"),
            away_team=d.get("away_team", "unknown"),
            competition=d.get("competition", "unknown"),
            round=d.get("round", "unknown"),
            score=score,
            venue=d.get("venue", "unknown"),
            context=d.get("context", {}),
        )


# ---------------------------------------------------------------------------
# PlayState
# ---------------------------------------------------------------------------

@dataclass
class Position2D:
    """Posição 2D no campo (x: 0–105m, y: 0–68m conforme padrão FIFA)."""
    x: float = 0.0
    y: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Position2D":
        return cls(x=float(d.get("x", 0.0)), y=float(d.get("y", 0.0)))

    def is_valid(self) -> bool:
        """Valida se a posição está dentro dos limites do campo (105x68m)."""
        return 0.0 <= self.x <= 105.0 and 0.0 <= self.y <= 68.0


@dataclass
class PlayerState:
    """Estado de um jogador em um determinado momento da partida."""
    player_id: str = "unknown"
    position: Position2D = field(default_factory=Position2D)
    team: str = "unknown"
    jersey_number: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "position": self.position.to_dict(),
            "team": self.team,
            "jersey_number": self.jersey_number,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PlayerState":
        return cls(
            player_id=d.get("player_id", "unknown"),
            position=Position2D.from_dict(d.get("position", {})),
            team=d.get("team", "unknown"),
            jersey_number=d.get("jersey_number"),
        )


@dataclass
class PlayState:
    """
    Estado de um lance em um determinado momento da partida.

    Campos:
        state_id: Identificador único do estado.
        match_id: ID da partida.
        timestamp: Segundo do jogo (ex: 2700 = 45min).
        phase: Fase de jogo.
        ball_position: Posição da bola.
        players: Lista de estados dos jogadores.
        possession_team: Time com a posse.
        game_state: Estado do placar para o time de referência.
        source: Fonte dos dados.
        confidence: Confiança da extração (0.0 a 1.0).
        needs_review: Marcado para revisão humana se confiança baixa.
    """
    state_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    match_id: str = "unknown"
    timestamp: float = 0.0
    phase: MatchPhase = MatchPhase.UNKNOWN
    ball_position: Position2D = field(default_factory=Position2D)
    players: List[PlayerState] = field(default_factory=list)
    possession_team: str = "unknown"
    game_state: GameState = GameState.UNKNOWN
    source: DataSource = DataSource.UNKNOWN
    confidence: float = 0.0
    needs_review: bool = False

    REVIEW_THRESHOLD: float = 0.7  # Confiança mínima para não precisar de revisão

    def __post_init__(self) -> None:
        # Sinaliza automaticamente para revisão se confiança abaixo do limiar
        if self.confidence < self.REVIEW_THRESHOLD:
            self.needs_review = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "match_id": self.match_id,
            "timestamp": self.timestamp,
            "phase": self.phase.value,
            "ball_position": self.ball_position.to_dict(),
            "players": [p.to_dict() for p in self.players],
            "possession_team": self.possession_team,
            "game_state": self.game_state.value,
            "source": self.source.value,
            "confidence": self.confidence,
            "needs_review": self.needs_review,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PlayState":
        phase_val = d.get("phase", "unknown")
        try:
            phase = MatchPhase(phase_val)
        except ValueError:
            raise ValueError(
                f"phase inválida: '{phase_val}'. "
                f"Valores válidos: {[p.value for p in MatchPhase]}"
            )

        game_state_val = d.get("game_state", "unknown")
        try:
            game_state = GameState(game_state_val)
        except ValueError:
            raise ValueError(
                f"game_state inválido: '{game_state_val}'. "
                f"Valores válidos: {[g.value for g in GameState]}"
            )

        source_val = d.get("source", "unknown")
        try:
            source = DataSource(source_val)
        except ValueError:
            raise ValueError(
                f"source inválida: '{source_val}'. "
                f"Valores válidos: {[s.value for s in DataSource]}"
            )

        return cls(
            state_id=d.get("state_id", str(uuid.uuid4())),
            match_id=d.get("match_id", "unknown"),
            timestamp=float(d.get("timestamp", 0.0)),
            phase=phase,
            ball_position=Position2D.from_dict(d.get("ball_position", {})),
            players=[PlayerState.from_dict(p) for p in d.get("players", [])],
            possession_team=d.get("possession_team", "unknown"),
            game_state=game_state,
            source=source,
            confidence=float(d.get("confidence", 0.0)),
            needs_review=d.get("needs_review", False),
        )


# ---------------------------------------------------------------------------
# TacticalBranch
# ---------------------------------------------------------------------------

@dataclass
class TacticalBranch:
    """
    Ramo tático alternativo gerado a partir de um PlayState.

    O score é calculado externamente pelo engine — não é inventado aqui.
    Campos de score são None até que o engine os preencha.

    score = opportunity_score + xT_delta + tactical_fit
            - transition_risk - physical_violation_penalty - uncertainty_penalty
    """
    branch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_state_id: str = "unknown"
    strategy: str = ""
    actions: List[str] = field(default_factory=list)
    score: Optional[float] = None
    risk: Optional[float] = None
    xt_delta: Optional[float] = None
    explanation: str = ""
    physical_validity: bool = True
    confidence: float = 0.0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "branch_id": self.branch_id,
            "source_state_id": self.source_state_id,
            "strategy": self.strategy,
            "actions": self.actions,
            "score": self.score,
            "risk": self.risk,
            "xt_delta": self.xt_delta,
            "explanation": self.explanation,
            "physical_validity": self.physical_validity,
            "confidence": self.confidence,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TacticalBranch":
        return cls(
            branch_id=d.get("branch_id", str(uuid.uuid4())),
            source_state_id=d.get("source_state_id", "unknown"),
            strategy=d.get("strategy", ""),
            actions=d.get("actions", []),
            score=d.get("score"),
            risk=d.get("risk"),
            xt_delta=d.get("xt_delta"),
            explanation=d.get("explanation", ""),
            physical_validity=bool(d.get("physical_validity", True)),
            confidence=float(d.get("confidence", 0.0)),
            tags=d.get("tags", []),
        )


# ---------------------------------------------------------------------------
# SquadProfile
# ---------------------------------------------------------------------------

@dataclass
class PositionDepth:
    """Profundidade de uma posição no elenco."""
    position: str = "unknown"
    players: List[str] = field(default_factory=list)   # Lista de player_ids
    depth_count: int = 0
    has_gap: bool = False
    gap_reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "players": self.players,
            "depth_count": self.depth_count,
            "has_gap": self.has_gap,
            "gap_reason": self.gap_reason,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PositionDepth":
        return cls(
            position=d.get("position", "unknown"),
            players=d.get("players", []),
            depth_count=int(d.get("depth_count", 0)),
            has_gap=bool(d.get("has_gap", False)),
            gap_reason=d.get("gap_reason", ""),
        )


@dataclass
class SquadProfile:
    """
    Perfil do elenco de uma equipe em uma temporada.

    Campos:
        team_id: ID da equipe.
        season: Temporada.
        roles_covered: Papéis táticos cobertos pelo elenco.
        role_gaps: Lacunas de papéis táticos.
        depth_by_position: Profundidade por posição.
        age_curve: Distribuição etária (ex: {"U23": 5, "23-29": 12, "30+": 4}).
        availability_flags: Jogadores com flags de disponibilidade.
    """
    team_id: str = "unknown"
    season: str = "unknown"
    roles_covered: List[str] = field(default_factory=list)
    role_gaps: List[str] = field(default_factory=list)
    depth_by_position: List[PositionDepth] = field(default_factory=list)
    age_curve: Dict[str, int] = field(default_factory=dict)
    availability_flags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "team_id": self.team_id,
            "season": self.season,
            "roles_covered": self.roles_covered,
            "role_gaps": self.role_gaps,
            "depth_by_position": [d.to_dict() for d in self.depth_by_position],
            "age_curve": self.age_curve,
            "availability_flags": self.availability_flags,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SquadProfile":
        return cls(
            team_id=d.get("team_id", "unknown"),
            season=d.get("season", "unknown"),
            roles_covered=d.get("roles_covered", []),
            role_gaps=d.get("role_gaps", []),
            depth_by_position=[
                PositionDepth.from_dict(p) for p in d.get("depth_by_position", [])
            ],
            age_curve=d.get("age_curve", {}),
            availability_flags=d.get("availability_flags", {}),
        )


# ---------------------------------------------------------------------------
# OpponentProfile
# ---------------------------------------------------------------------------

@dataclass
class SetPieceProfile:
    """Perfil de bola parada de uma equipe."""
    corners_routine: str = "unknown"
    free_kick_routine: str = "unknown"
    defensive_set_piece: str = "unknown"
    key_takers: List[str] = field(default_factory=list)
    key_targets: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "corners_routine": self.corners_routine,
            "free_kick_routine": self.free_kick_routine,
            "defensive_set_piece": self.defensive_set_piece,
            "key_takers": self.key_takers,
            "key_targets": self.key_targets,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SetPieceProfile":
        return cls(
            corners_routine=d.get("corners_routine", "unknown"),
            free_kick_routine=d.get("free_kick_routine", "unknown"),
            defensive_set_piece=d.get("defensive_set_piece", "unknown"),
            key_takers=d.get("key_takers", []),
            key_targets=d.get("key_targets", []),
            notes=d.get("notes", ""),
        )


@dataclass
class OpponentProfile:
    """
    Perfil de um adversário para preparação de jogo.

    Campos:
        opponent_id: ID do adversário (team_id).
        formation_patterns: Formações observadas (ex: ["4-4-2", "4-3-3"]).
        pressing_profile: Descrição do pressing.
        weak_zones: Zonas de vulnerabilidade identificadas.
        transition_vulnerabilities: Vulnerabilidades em transição.
        set_piece_profile: Perfil de bola parada.
        last_updated: Data da última atualização da análise.
        source_matches: IDs das partidas usadas na análise.
    """
    opponent_id: str = "unknown"
    formation_patterns: List[str] = field(default_factory=list)
    pressing_profile: str = "unknown"
    weak_zones: List[str] = field(default_factory=list)
    transition_vulnerabilities: List[str] = field(default_factory=list)
    set_piece_profile: SetPieceProfile = field(default_factory=SetPieceProfile)
    last_updated: Optional[str] = None
    source_matches: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "opponent_id": self.opponent_id,
            "formation_patterns": self.formation_patterns,
            "pressing_profile": self.pressing_profile,
            "weak_zones": self.weak_zones,
            "transition_vulnerabilities": self.transition_vulnerabilities,
            "set_piece_profile": self.set_piece_profile.to_dict(),
            "last_updated": self.last_updated,
            "source_matches": self.source_matches,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "OpponentProfile":
        return cls(
            opponent_id=d.get("opponent_id", "unknown"),
            formation_patterns=d.get("formation_patterns", []),
            pressing_profile=d.get("pressing_profile", "unknown"),
            weak_zones=d.get("weak_zones", []),
            transition_vulnerabilities=d.get("transition_vulnerabilities", []),
            set_piece_profile=SetPieceProfile.from_dict(d.get("set_piece_profile", {})),
            last_updated=d.get("last_updated"),
            source_matches=d.get("source_matches", []),
        )


# ---------------------------------------------------------------------------
# ScoutingTarget
# ---------------------------------------------------------------------------

@dataclass
class ScoutingTarget:
    """
    Alvo de scouting para contratação.

    Campos:
        player_id: ID do jogador-alvo.
        current_club: Clube atual.
        role_fit: Encaixe de papel tático (0.0 a 1.0 — calculado externamente).
        tactical_fit: Encaixe tático geral (0.0 a 1.0 — calculado externamente).
        cost_range: Faixa de custo estimado (ex: "€5M–€8M").
        risk_flags: Flags de risco (ex: ["injury_history", "adaptation_risk"]).
        recommendation_level: Nível de recomendação.
        squad_need: Necessidade do elenco que o jogador atenderia.
        notes: Observações do scout.
    """
    player_id: str = "unknown"
    current_club: str = "unknown"
    role_fit: Optional[float] = None
    tactical_fit: Optional[float] = None
    cost_range: str = "unknown"
    risk_flags: List[str] = field(default_factory=list)
    recommendation_level: RecommendationLevel = RecommendationLevel.WEAK
    squad_need: str = ""
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "current_club": self.current_club,
            "role_fit": self.role_fit,
            "tactical_fit": self.tactical_fit,
            "cost_range": self.cost_range,
            "risk_flags": self.risk_flags,
            "recommendation_level": self.recommendation_level.value,
            "squad_need": self.squad_need,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ScoutingTarget":
        rec_val = d.get("recommendation_level", "weak")
        try:
            rec = RecommendationLevel(rec_val)
        except ValueError:
            raise ValueError(
                f"recommendation_level inválido: '{rec_val}'. "
                f"Valores válidos: {[r.value for r in RecommendationLevel]}"
            )
        return cls(
            player_id=d.get("player_id", "unknown"),
            current_club=d.get("current_club", "unknown"),
            role_fit=d.get("role_fit"),
            tactical_fit=d.get("tactical_fit"),
            cost_range=d.get("cost_range", "unknown"),
            risk_flags=d.get("risk_flags", []),
            recommendation_level=rec,
            squad_need=d.get("squad_need", ""),
            notes=d.get("notes", ""),
        )


# ---------------------------------------------------------------------------
# DecisionReport
# ---------------------------------------------------------------------------

@dataclass
class Tradeoff:
    """Tradeoff de uma decisão: o que se ganha e o que se perde."""
    gain: str = ""
    cost: str = ""
    context: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"gain": self.gain, "cost": self.cost, "context": self.context}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Tradeoff":
        return cls(
            gain=d.get("gain", ""),
            cost=d.get("cost", ""),
            context=d.get("context", ""),
        )


@dataclass
class DecisionReport:
    """
    Relatório de decisão gerado pelo sistema.

    Campos:
        report_id: Identificador único do relatório.
        created_at: Data/hora de criação.
        inputs: Inputs que geraram o relatório.
        recommendations: Lista de recomendações (fato + inferência separados).
        tradeoffs: Tradeoffs identificados.
        risks: Riscos identificados.
        confidence: Confiança geral do relatório (0.0 a 1.0).
        human_feedback: Feedback humano registrado.
        next_actions: Ações sugeridas.
        explanation: Explicação do processo de decisão.
        reviewed_by: Nome do revisor humano.
        reviewed_at: Data/hora da revisão.
    """
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )
    inputs: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    tradeoffs: List[Tradeoff] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    confidence: Optional[float] = None
    human_feedback: Optional[str] = None
    next_actions: List[str] = field(default_factory=list)
    explanation: str = ""
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "created_at": self.created_at,
            "inputs": self.inputs,
            "recommendations": self.recommendations,
            "tradeoffs": [t.to_dict() for t in self.tradeoffs],
            "risks": self.risks,
            "confidence": self.confidence,
            "human_feedback": self.human_feedback,
            "next_actions": self.next_actions,
            "explanation": self.explanation,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DecisionReport":
        return cls(
            report_id=d.get("report_id", str(uuid.uuid4())),
            created_at=d.get("created_at", datetime.utcnow().isoformat() + "Z"),
            inputs=d.get("inputs", {}),
            recommendations=d.get("recommendations", []),
            tradeoffs=[Tradeoff.from_dict(t) for t in d.get("tradeoffs", [])],
            risks=d.get("risks", []),
            confidence=d.get("confidence"),
            human_feedback=d.get("human_feedback"),
            next_actions=d.get("next_actions", []),
            explanation=d.get("explanation", ""),
            reviewed_by=d.get("reviewed_by"),
            reviewed_at=d.get("reviewed_at"),
        )
