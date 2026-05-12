"""
squad_fixtures.py — Fixtures de elenco para demonstração e testes.

IMPORTANTE: Estes dados são FICTÍCIOS e servem apenas para demonstração
do sistema. Não representam o elenco real do São Paulo FC.

Todo fixture é marcado com tag 'fixture' para rastreabilidade.
Princípio: Não inventar dados reais — fixtures são claramente identificadas.
"""
from __future__ import annotations

from typing import List

from src.core.football_models import (
    AvailabilityStatus,
    Foot,
    Player,
)


def build_demo_squad() -> List[Player]:
    """
    Constrói um elenco de demonstração fictício com estrutura 4-3-3.

    AVISO: Dados completamente fictícios para fins de demonstração do sistema.
    Nomes, idades e atributos são inventados e não representam jogadores reais.
    """
    return [
        # Goleiros
        Player(
            player_id="demo-gk-01",
            name="[Demo] Goleiro Titular",
            age=28,
            preferred_foot=Foot.RIGHT,
            positions=["GK"],
            roles=["gk"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        Player(
            player_id="demo-gk-02",
            name="[Demo] Goleiro Reserva",
            age=24,
            preferred_foot=Foot.RIGHT,
            positions=["GK"],
            roles=["gk"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        # Zagueiros
        Player(
            player_id="demo-cb-01",
            name="[Demo] Zagueiro Construtor",
            age=30,
            preferred_foot=Foot.RIGHT,
            positions=["CB"],
            roles=["ball_playing_cb"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        Player(
            player_id="demo-cb-02",
            name="[Demo] Zagueiro Marcador",
            age=27,
            preferred_foot=Foot.LEFT,
            positions=["CB"],
            roles=["stopper_cb"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        Player(
            player_id="demo-cb-03",
            name="[Demo] Zagueiro Reserva",
            age=22,
            preferred_foot=Foot.RIGHT,
            positions=["CB"],
            roles=["ball_playing_cb", "stopper_cb"],
            availability_status=AvailabilityStatus.INJURED,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício. Lesionado para demonstrar gap.",
        ),
        # Laterais
        Player(
            player_id="demo-rb-01",
            name="[Demo] Lateral Direito Titular",
            age=26,
            preferred_foot=Foot.RIGHT,
            positions=["RB"],
            roles=["attacking_rb"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        Player(
            player_id="demo-rb-02",
            name="[Demo] Lateral Direito Reserva",
            age=21,
            preferred_foot=Foot.RIGHT,
            positions=["RB", "CB"],
            roles=["attacking_rb"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        Player(
            player_id="demo-lb-01",
            name="[Demo] Lateral Esquerdo Titular",
            age=25,
            preferred_foot=Foot.LEFT,
            positions=["LB"],
            roles=["attacking_lb"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        # Sem reserva de lateral esquerdo — para demonstrar gap moderado
        # Volantes
        Player(
            player_id="demo-dm-01",
            name="[Demo] Volante Destruidor",
            age=29,
            preferred_foot=Foot.RIGHT,
            positions=["DM"],
            roles=["defensive_mid"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        Player(
            player_id="demo-dm-02",
            name="[Demo] Volante Reserva",
            age=23,
            preferred_foot=Foot.RIGHT,
            positions=["DM", "CM"],
            roles=["defensive_mid", "box_to_box_mid"],
            availability_status=AvailabilityStatus.SUSPENDED,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício. Suspenso para demonstrar gap.",
        ),
        # Meias
        Player(
            player_id="demo-cm-01",
            name="[Demo] Meia Box-to-Box",
            age=27,
            preferred_foot=Foot.RIGHT,
            positions=["CM"],
            roles=["box_to_box_mid"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Argentino",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        Player(
            player_id="demo-cm-02",
            name="[Demo] Meia Criativo",
            age=24,
            preferred_foot=Foot.LEFT,
            positions=["CM", "AM"],
            roles=["creative_mid"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        Player(
            player_id="demo-cm-03",
            name="[Demo] Meia Reserva",
            age=20,
            preferred_foot=Foot.RIGHT,
            positions=["CM"],
            roles=["box_to_box_mid", "creative_mid"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        # Extremos
        Player(
            player_id="demo-rw-01",
            name="[Demo] Extremo Direito Titular",
            age=22,
            preferred_foot=Foot.LEFT,
            positions=["RW"],
            roles=["winger_right"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        Player(
            player_id="demo-rw-02",
            name="[Demo] Extremo Direito Reserva",
            age=19,
            preferred_foot=Foot.RIGHT,
            positions=["RW", "ST"],
            roles=["winger_right"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        Player(
            player_id="demo-lw-01",
            name="[Demo] Extremo Esquerdo Titular",
            age=25,
            preferred_foot=Foot.RIGHT,
            positions=["LW"],
            roles=["winger_left"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Colombiano",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        Player(
            player_id="demo-lw-02",
            name="[Demo] Extremo Esquerdo Reserva",
            age=21,
            preferred_foot=Foot.LEFT,
            positions=["LW", "RW"],
            roles=["winger_left", "winger_right"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        # Centroavantes
        Player(
            player_id="demo-st-01",
            name="[Demo] Centroavante Titular",
            age=31,
            preferred_foot=Foot.RIGHT,
            positions=["ST"],
            roles=["striker"],
            availability_status=AvailabilityStatus.AVAILABLE,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício.",
        ),
        Player(
            player_id="demo-st-02",
            name="[Demo] Centroavante Reserva",
            age=23,
            preferred_foot=Foot.RIGHT,
            positions=["ST", "CF"],
            roles=["striker"],
            availability_status=AvailabilityStatus.DOUBTFUL,
            nationality="Brasileiro",
            current_club="São Paulo FC (Demo)",
            notes="Fixture de demonstração — dado fictício. Dúvida para demonstrar alerta.",
        ),
    ]
