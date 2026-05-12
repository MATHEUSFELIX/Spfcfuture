"""
opponent_fixtures.py — Fixtures de Adversários para Demonstração.

AVISO: Todos os dados neste arquivo são FICTÍCIOS e criados exclusivamente
para demonstração do sistema. Não representam dados reais de nenhum clube.
Nenhum dado de desempenho, tático ou estatístico foi inventado como real.

Os adversários são identificados como [Demo] e suas análises são marcadas
explicitamente como fixtures de demonstração.
"""
from __future__ import annotations

from typing import List

from src.core.football_models import OpponentProfile, SetPieceProfile


def build_demo_opponents() -> List[dict]:
    """
    Retorna uma lista de adversários de demonstração com seus perfis.

    Cada item contém:
        - profile: OpponentProfile com dados fictícios
        - name: Nome de exibição do adversário
        - description: Descrição do adversário (fictícia)

    Returns:
        Lista de dicts com profile, name e description.
    """
    return [
        _build_opponent_high_pressing(),
        _build_opponent_low_block(),
        _build_opponent_counter_attack(),
    ]


def get_demo_opponent_by_id(opponent_id: str) -> dict | None:
    """
    Retorna um adversário de demonstração pelo ID.

    Args:
        opponent_id: ID do adversário.

    Returns:
        Dict com profile, name e description, ou None se não encontrado.
    """
    opponents = build_demo_opponents()
    for opp in opponents:
        if opp["profile"].opponent_id == opponent_id:
            return opp
    return None


# ---------------------------------------------------------------------------
# Adversário 1: Pressing Alto
# ---------------------------------------------------------------------------

def _build_opponent_high_pressing() -> dict:
    """
    Adversário de demonstração com pressing alto e linha defensiva elevada.
    Dados 100% fictícios — marcados como [Demo].
    """
    profile = OpponentProfile(
        opponent_id="demo-opp-001",
        formation_patterns=["4-3-3", "4-2-3-1"],
        pressing_profile=(
            "high intensity pressing with high defensive line. "
            "Triggers pressing in the opponent's defensive third. "
            "Fast recovery after losing possession."
        ),
        weak_zones=[
            "Espaço nas costas da linha defensiva alta (critical) — "
            "vulnerável a bolas em profundidade.",
            "Corredor direito (right) após sobreposição do lateral-esquerdo — "
            "desequilíbrio defensivo identificado.",
            "Zona central entre as linhas (center) quando o volante avança — "
            "espaço para o meia criativo (moderate).",
        ],
        transition_vulnerabilities=[
            "Transição defensiva (defensive) após perda no campo ofensivo — "
            "linha alta cria espaço crítico para contra-ataque.",
            "Recuperação lenta do lateral-esquerdo em transição defensiva — "
            "vulnerabilidade no corredor direito adversário.",
        ],
        set_piece_profile=SetPieceProfile(
            corners_routine=(
                "Escanteios curtos para triangulação na entrada da área. "
                "Cobrador principal: Jogador 10 [Demo]."
            ),
            free_kick_routine=(
                "Faltas diretas com cobrador especialista. "
                "Variação: cruzamento para segundo pau."
            ),
            defensive_set_piece=(
                "Marcação por zona com um jogador na bola. "
                "Fraqueza: segundo pau desguarnecido em escanteios."
            ),
            key_takers=["Jogador 10 [Demo]", "Jogador 7 [Demo]"],
            key_targets=["Jogador 9 [Demo]", "Jogador 5 [Demo]"],
            notes="Dados fictícios — fixture de demonstração.",
        ),
        source_matches=[
            "demo-match-001",
            "demo-match-002",
            "demo-match-003",
            "demo-match-004",
        ],
        last_updated="2025-01-01",
    )

    return {
        "profile": profile,
        "name": "Adversário Pressing Alto [Demo]",
        "description": (
            "Equipe de demonstração que representa um adversário com pressing "
            "de alta intensidade e linha defensiva elevada. "
            "Dados 100% fictícios para fins de demonstração do sistema."
        ),
    }


# ---------------------------------------------------------------------------
# Adversário 2: Bloco Baixo
# ---------------------------------------------------------------------------

def _build_opponent_low_block() -> dict:
    """
    Adversário de demonstração com bloco baixo e contra-ataque direto.
    Dados 100% fictícios — marcados como [Demo].
    """
    profile = OpponentProfile(
        opponent_id="demo-opp-002",
        formation_patterns=["4-4-2", "5-4-1"],
        pressing_profile=(
            "low intensity pressing with low defensive line. "
            "Organized defensive block in own half. "
            "Slow recovery speed — relies on defensive organization."
        ),
        weak_zones=[
            "Corredor esquerdo (left) — lateral-direito adversário lento na recuperação (moderate).",
            "Zona central entre as linhas (center) — bloco compacto mas espaço no meio (low).",
        ],
        transition_vulnerabilities=[
            "Transição ofensiva (offensive) após recuperação de bola — "
            "equipe demora a se reorganizar para contra-atacar.",
        ],
        set_piece_profile=SetPieceProfile(
            corners_routine=(
                "Escanteios diretos para a área. "
                "Buscam o segundo pau com jogadores de altura."
            ),
            free_kick_routine=(
                "Faltas laterais cruzadas para a área. "
                "Sem cobrador especialista identificado."
            ),
            defensive_set_piece=(
                "Marcação por zona. "
                "Organização defensiva sólida em bola parada."
            ),
            key_takers=["Jogador 8 [Demo]"],
            key_targets=["Jogador 9 [Demo]", "Jogador 4 [Demo]"],
            notes="Dados fictícios — fixture de demonstração.",
        ),
        source_matches=[
            "demo-match-005",
            "demo-match-006",
        ],
        last_updated="2025-01-01",
    )

    return {
        "profile": profile,
        "name": "Adversário Bloco Baixo [Demo]",
        "description": (
            "Equipe de demonstração que representa um adversário com bloco "
            "baixo organizado e contra-ataque direto. "
            "Dados 100% fictícios para fins de demonstração do sistema."
        ),
    }


# ---------------------------------------------------------------------------
# Adversário 3: Contra-Ataque
# ---------------------------------------------------------------------------

def _build_opponent_counter_attack() -> dict:
    """
    Adversário de demonstração com pressing médio e contra-ataque rápido.
    Dados 100% fictícios — marcados como [Demo].
    """
    profile = OpponentProfile(
        opponent_id="demo-opp-003",
        formation_patterns=["4-4-2", "4-3-3"],
        pressing_profile=(
            "medium intensity pressing with medium defensive line. "
            "Selective pressing in middle third. "
            "Fast counter-attack after winning possession."
        ),
        weak_zones=[
            "Corredor direito (right) — lateral-esquerdo adversário avança muito (high).",
            "Espaço entre linhas (center) — volante único deixa zona descoberta (moderate).",
        ],
        transition_vulnerabilities=[
            "Transição defensiva (defensive) após avanço do lateral-esquerdo — "
            "corredor direito adversário fica exposto (alta severidade).",
        ],
        set_piece_profile=SetPieceProfile(
            corners_routine=(
                "Escanteios variados: curto e direto. "
                "Cobrador: Jogador 11 [Demo]."
            ),
            free_kick_routine=(
                "Faltas diretas com dois cobradores. "
                "Variação: tabela na barreira."
            ),
            defensive_set_piece=(
                "Marcação mista (zona + individual). "
                "Segundo pau vulnerável em escanteios (fraco)."
            ),
            key_takers=["Jogador 11 [Demo]", "Jogador 6 [Demo]"],
            key_targets=["Jogador 9 [Demo]"],
            notes="Dados fictícios — fixture de demonstração.",
        ),
        source_matches=[
            "demo-match-007",
            "demo-match-008",
            "demo-match-009",
        ],
        last_updated="2025-01-01",
    )

    return {
        "profile": profile,
        "name": "Adversário Contra-Ataque [Demo]",
        "description": (
            "Equipe de demonstração que representa um adversário com pressing "
            "médio e transição ofensiva rápida. "
            "Dados 100% fictícios para fins de demonstração do sistema."
        ),
    }
