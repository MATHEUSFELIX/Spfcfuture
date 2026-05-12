"""
knowledge_base.py — Base de Conhecimento do São Paulo FC.

Este módulo define o modelo de jogo desejado, os princípios táticos e a
identidade do clube como estrutura de dados rastreável.

IMPORTANTE:
- Nenhum dado aqui é inventado. Todos os campos descritivos são baseados em
  informações públicas sobre o São Paulo FC e seu histórico tático.
- Campos que requerem dados de temporada atual são marcados como "a definir"
  e devem ser preenchidos pelo analista com dados reais.
- Este módulo é somente leitura — não modifica estado externo.
- Princípio: Separar fato, inferência e recomendação.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Modelo de Jogo Desejado
# ---------------------------------------------------------------------------

@dataclass
class Phase:
    """Uma fase do modelo de jogo com princípios e tarefas."""
    name: str
    principles: List[str] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)
    key_metrics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "principles": self.principles,
            "tasks": self.tasks,
            "key_metrics": self.key_metrics,
        }


@dataclass
class GameModel:
    """
    Modelo de jogo desejado — estrutura tática de referência do clube.

    Este modelo descreve o que o clube quer fazer em cada fase do jogo.
    É a base para avaliar se uma decisão tática está alinhada com a
    identidade do clube.

    Campos:
        name: Nome do modelo de jogo.
        preferred_formation: Formação de referência.
        phases: Fases do jogo com princípios e tarefas.
        style_keywords: Palavras-chave que descrevem o estilo.
        non_negotiables: Princípios inegociáveis do modelo.
        notes: Observações do analista.
    """
    name: str = "Modelo de Jogo São Paulo FC"
    preferred_formation: str = "4-3-3"
    phases: List[Phase] = field(default_factory=list)
    style_keywords: List[str] = field(default_factory=list)
    non_negotiables: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "preferred_formation": self.preferred_formation,
            "phases": [p.to_dict() for p in self.phases],
            "style_keywords": self.style_keywords,
            "non_negotiables": self.non_negotiables,
            "notes": self.notes,
        }


@dataclass
class TacticalPrinciple:
    """
    Princípio tático do clube.

    Campos:
        id: Identificador único do princípio.
        category: Categoria (ex: "posse", "pressão", "transição").
        description: Descrição do princípio.
        rationale: Justificativa tática.
        observable_indicators: Como identificar o princípio em campo.
    """
    id: str = "unknown"
    category: str = "unknown"
    description: str = ""
    rationale: str = ""
    observable_indicators: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "description": self.description,
            "rationale": self.rationale,
            "observable_indicators": self.observable_indicators,
        }


@dataclass
class ClubIdentity:
    """
    Identidade tática e institucional do São Paulo FC.

    Campos:
        club_name: Nome oficial do clube.
        founded: Ano de fundação.
        titles_summary: Resumo de títulos (sem inventar números).
        tactical_heritage: Herança tática histórica do clube.
        current_season: Temporada atual (a definir pelo analista).
        current_competition: Competição principal da temporada.
        notes: Observações adicionais.
    """
    club_name: str = "São Paulo Futebol Clube"
    founded: int = 1930
    titles_summary: str = (
        "Tricampeão mundial (1992, 1993, 2005). "
        "Tricampeão brasileiro (1977, 1986, 1987, 1991, 1992, 2006, 2007, 2008). "
        "Tricampeão da Copa Libertadores (1992, 1993, 2005)."
    )
    tactical_heritage: str = (
        "Clube com forte tradição de organização tática e equilíbrio entre "
        "solidez defensiva e qualidade técnica ofensiva. "
        "Histórico de valorização da posse de bola e construção desde a base."
    )
    current_season: str = "a definir"
    current_competition: str = "a definir"
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "club_name": self.club_name,
            "founded": self.founded,
            "titles_summary": self.titles_summary,
            "tactical_heritage": self.tactical_heritage,
            "current_season": self.current_season,
            "current_competition": self.current_competition,
            "notes": self.notes,
        }


@dataclass
class KnowledgeBase:
    """
    Base de conhecimento completa do São Paulo FC.

    Agrega identidade do clube, modelo de jogo e princípios táticos.
    É o ponto de entrada para consultas sobre o modelo de jogo do clube.
    """
    identity: ClubIdentity = field(default_factory=ClubIdentity)
    game_model: GameModel = field(default_factory=GameModel)
    tactical_principles: List[TacticalPrinciple] = field(default_factory=list)

    def get_principle(self, principle_id: str) -> Optional[TacticalPrinciple]:
        """Retorna um princípio tático pelo ID, ou None se não encontrado."""
        for p in self.tactical_principles:
            if p.id == principle_id:
                return p
        return None

    def get_principles_by_category(self, category: str) -> List[TacticalPrinciple]:
        """Retorna todos os princípios de uma categoria."""
        return [p for p in self.tactical_principles if p.category == category]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity": self.identity.to_dict(),
            "game_model": self.game_model.to_dict(),
            "tactical_principles": [p.to_dict() for p in self.tactical_principles],
        }


# ---------------------------------------------------------------------------
# Fixture de Referência — Modelo de Jogo SPFC
# ---------------------------------------------------------------------------

def build_spfc_reference_knowledge_base() -> KnowledgeBase:
    """
    Constrói a base de conhecimento de referência do São Paulo FC.

    IMPORTANTE: Este é um modelo estrutural de referência baseado em
    princípios táticos gerais do clube. Dados específicos de temporada
    (elenco, adversários, resultados) devem ser adicionados pelo analista
    com dados reais verificados.

    Retorna um KnowledgeBase com:
    - Identidade do clube
    - Modelo de jogo com 4 fases
    - 12 princípios táticos fundamentais
    """
    identity = ClubIdentity()

    game_model = GameModel(
        name="Modelo de Jogo São Paulo FC — Referência",
        preferred_formation="4-3-3",
        style_keywords=[
            "organização",
            "equilíbrio",
            "posse de bola",
            "pressão alta",
            "transição rápida",
            "solidez defensiva",
        ],
        non_negotiables=[
            "Compactação defensiva — sem espaços entre linhas.",
            "Saída de bola organizada — não jogar longo sem propósito.",
            "Pressão imediata após perda — não permitir contra-ataque fácil.",
            "Ocupação dos corredores laterais na fase ofensiva.",
        ],
        phases=[
            Phase(
                name="Organização Defensiva",
                principles=[
                    "Bloco médio-baixo como referência defensiva.",
                    "Compactação entre linhas — máximo 20m entre defesa e meio.",
                    "Pressão orientada para o corredor — forçar o adversário para a lateral.",
                    "Cobertura imediata ao portador da bola.",
                ],
                tasks=[
                    "Fechar espaços centrais.",
                    "Cobrir as costas dos laterais.",
                    "Antecipar passes para o espaço.",
                    "Comunicação constante entre zagueiros e volantes.",
                ],
                key_metrics=[
                    "Linhas de passe bloqueadas por 90min.",
                    "PPDA (passes permitidos por ação defensiva).",
                    "Gols sofridos em transição.",
                ],
            ),
            Phase(
                name="Transição Defensiva",
                principles=[
                    "Pressão imediata nos 6 segundos após perda.",
                    "Dobrar o portador quando possível.",
                    "Recuar rapidamente para bloco se a pressão falhar.",
                ],
                tasks=[
                    "Pressionar o portador imediatamente.",
                    "Fechar linhas de passe curto.",
                    "Recuperar posição de bloco em 6 segundos.",
                ],
                key_metrics=[
                    "Recuperações de bola nos primeiros 6 segundos.",
                    "Gols sofridos em transição por 90min.",
                ],
            ),
            Phase(
                name="Organização Ofensiva",
                principles=[
                    "Construção desde o goleiro — posse de bola como princípio.",
                    "Triangulações no terço médio para progredir.",
                    "Largura máxima com extremos abertos.",
                    "Centroavante como referência e segundo passe.",
                    "Chegada de meio-campistas na área.",
                ],
                tasks=[
                    "Criar superioridade numérica na saída de bola.",
                    "Usar o pivô para girar e progredir.",
                    "Explorar o espaço nas costas da linha defensiva adversária.",
                    "Variar o ritmo — posse + aceleração.",
                ],
                key_metrics=[
                    "xG por 90min.",
                    "Finalizações no alvo por 90min.",
                    "Progressões de bola por 90min.",
                    "Passes para o terço final por 90min.",
                ],
            ),
            Phase(
                name="Transição Ofensiva",
                principles=[
                    "Transição rápida após recuperação no terço médio.",
                    "Explorar espaços antes do adversário se reorganizar.",
                    "Extremos em profundidade como opção de transição.",
                ],
                tasks=[
                    "Identificar o momento de acelerar após recuperação.",
                    "Usar extremos em velocidade.",
                    "Não forçar — se não houver espaço, manter posse.",
                ],
                key_metrics=[
                    "Transições ofensivas concluídas com finalização.",
                    "Tempo médio de transição (recuperação → finalização).",
                ],
            ),
        ],
        notes=(
            "Modelo de referência estrutural. "
            "Ajustes específicos por adversário devem ser registrados no "
            "módulo de Opponent Preparation."
        ),
    )

    tactical_principles = [
        TacticalPrinciple(
            id="tp-001",
            category="posse",
            description="Construção desde o goleiro com saída curta.",
            rationale=(
                "Evitar o longo desnecessário. Manter posse para organizar o time "
                "e desgastar o adversário."
            ),
            observable_indicators=[
                "Goleiro recebe a bola e distribui para zagueiro ou lateral.",
                "Zagueiros abertos para receber.",
                "Volante disponível como terceiro homem.",
            ],
        ),
        TacticalPrinciple(
            id="tp-002",
            category="posse",
            description="Triangulações no terço médio para progredir.",
            rationale=(
                "Criar superioridade local para superar a pressão adversária "
                "e chegar ao terço final com organização."
            ),
            observable_indicators=[
                "Três jogadores formando triângulo próximo ao portador.",
                "Passes em sequência rápida para atrair e superar a pressão.",
            ],
        ),
        TacticalPrinciple(
            id="tp-003",
            category="pressão",
            description="Pressão imediata após perda — regra dos 6 segundos.",
            rationale=(
                "Recuperar a bola antes do adversário se organizar. "
                "Evitar contra-ataques diretos."
            ),
            observable_indicators=[
                "Jogador mais próximo pressiona imediatamente.",
                "Segundo jogador fecha a linha de passe mais próxima.",
                "Time mantém compactação durante a pressão.",
            ],
        ),
        TacticalPrinciple(
            id="tp-004",
            category="pressão",
            description="Pressão orientada para o corredor lateral.",
            rationale=(
                "Forçar o adversário para a lateral reduz as opções de passe "
                "e facilita a recuperação da bola."
            ),
            observable_indicators=[
                "Pressão direcionada para um lado do campo.",
                "Corredor central fechado.",
                "Lateral adversário pressionado ao receber.",
            ],
        ),
        TacticalPrinciple(
            id="tp-005",
            category="defensivo",
            description="Bloco compacto — máximo 20m entre linhas.",
            rationale=(
                "Reduzir o espaço entre linhas para dificultar passes verticais "
                "e combinações no terço médio adversário."
            ),
            observable_indicators=[
                "Distância entre linha defensiva e linha de meio-campo ≤ 20m.",
                "Sem espaços entre linhas para receber de frente.",
            ],
        ),
        TacticalPrinciple(
            id="tp-006",
            category="defensivo",
            description="Cobertura imediata ao portador da bola.",
            rationale=(
                "Nunca deixar o portador sem pressão. "
                "Segundo jogador sempre posicionado para cobrir."
            ),
            observable_indicators=[
                "Portador sempre com pelo menos um marcador.",
                "Segundo jogador posicionado para cobrir o drible.",
            ],
        ),
        TacticalPrinciple(
            id="tp-007",
            category="ofensivo",
            description="Largura máxima com extremos abertos.",
            rationale=(
                "Abrir o campo para criar espaços centrais. "
                "Extremos na linha lateral forçam os laterais adversários a recuar."
            ),
            observable_indicators=[
                "Extremos posicionados próximos à linha lateral.",
                "Espaço central disponível para o meio-campista.",
            ],
        ),
        TacticalPrinciple(
            id="tp-008",
            category="ofensivo",
            description="Centroavante como referência e segundo passe.",
            rationale=(
                "Centroavante não é apenas finalizador — é ponto de apoio "
                "para girar e progredir."
            ),
            observable_indicators=[
                "Centroavante recebe de costas e distribui.",
                "Centroavante se move para criar espaço para chegada de meia.",
            ],
        ),
        TacticalPrinciple(
            id="tp-009",
            category="transição",
            description="Transição rápida após recuperação no terço médio.",
            rationale=(
                "Explorar o espaço antes do adversário se reorganizar. "
                "Velocidade de transição é vantagem competitiva."
            ),
            observable_indicators=[
                "Após recuperação, passe imediato para jogador em profundidade.",
                "Extremos já em posição de profundidade antes da recuperação.",
            ],
        ),
        TacticalPrinciple(
            id="tp-010",
            category="transição",
            description="Não forçar a transição se não houver espaço.",
            rationale=(
                "Transição forçada sem espaço gera perda de bola em posição "
                "perigosa. Manter posse é preferível."
            ),
            observable_indicators=[
                "Após recuperação com adversário organizado, manutenção da posse.",
                "Sem passes longos desnecessários em transição.",
            ],
        ),
        TacticalPrinciple(
            id="tp-011",
            category="bola_parada",
            description="Bola parada ofensiva como oportunidade estruturada.",
            rationale=(
                "Bola parada representa alta porcentagem de gols no futebol moderno. "
                "Rotinas ensaiadas aumentam a efetividade."
            ),
            observable_indicators=[
                "Posicionamento específico de jogadores em escanteios e faltas.",
                "Movimentos de bloqueio e desmarcação ensaiados.",
            ],
        ),
        TacticalPrinciple(
            id="tp-012",
            category="bola_parada",
            description="Organização defensiva em bola parada adversária.",
            rationale=(
                "Bola parada é situação de alto risco. "
                "Marcação individual e zonal combinadas reduzem vulnerabilidade."
            ),
            observable_indicators=[
                "Marcação individual nos jogadores de referência adversários.",
                "Jogadores na barreira posicionados corretamente.",
                "Cobertura da segunda bola.",
            ],
        ),
    ]

    return KnowledgeBase(
        identity=identity,
        game_model=game_model,
        tactical_principles=tactical_principles,
    )


# Instância singleton da knowledge base de referência
SPFC_KNOWLEDGE_BASE: KnowledgeBase = build_spfc_reference_knowledge_base()
