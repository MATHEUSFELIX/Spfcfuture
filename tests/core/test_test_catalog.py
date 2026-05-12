"""
Testes do Test Catalog — SPFC Champion Decision OS.

Categoria: API and CLI
Valida: integridade do catálogo de categorias de testes e explicabilidade.
"""
import pytest

from src.core.test_catalog import (
    TEST_CATALOG,
    TestCategory,
    get_catalog,
    get_category,
)

EXPECTED_CATEGORY_IDS = {
    "domain_models",
    "pipeline",
    "context_and_priors",
    "viewer",
    "video_to_state",
    "runtime_ingestion",
    "workflow_and_review",
    "governance_and_observability",
    "api_and_cli",
    "pilot_evaluation",
}


class TestGetCatalog:
    """Testes para a função get_catalog."""

    def test_returns_non_empty_list(self):
        """Garante que o catálogo não está vazio."""
        catalog = get_catalog()
        assert len(catalog) > 0

    def test_all_expected_categories_present(self):
        """Garante que todas as categorias obrigatórias estão presentes."""
        catalog = get_catalog()
        actual_ids = {cat.id for cat in catalog}
        for expected_id in EXPECTED_CATEGORY_IDS:
            assert expected_id in actual_ids, (
                f"Categoria '{expected_id}' ausente do catálogo. "
                "Todas as 10 categorias definidas em 06_APP_UX.md devem estar presentes."
            )

    def test_catalog_has_exactly_ten_categories(self):
        """Garante que o catálogo tem exatamente 10 categorias conforme spec."""
        catalog = get_catalog()
        assert len(catalog) == 10, (
            f"Esperado 10 categorias, encontrado {len(catalog)}. "
            "Conforme 06_APP_UX.md, o Test Health deve ter 10 categorias."
        )


class TestCategoryIntegrity:
    """Testes de integridade de cada categoria do catálogo."""

    @pytest.mark.parametrize("cat", TEST_CATALOG)
    def test_category_has_non_empty_id(self, cat: TestCategory):
        """Garante que cada categoria tem um ID não vazio."""
        assert cat.id != ""

    @pytest.mark.parametrize("cat", TEST_CATALOG)
    def test_category_has_non_empty_title(self, cat: TestCategory):
        """Garante que cada categoria tem um título não vazio."""
        assert cat.title != ""

    @pytest.mark.parametrize("cat", TEST_CATALOG)
    def test_category_has_what_it_validates(self, cat: TestCategory):
        """
        Garante que cada categoria explica o que valida.
        Princípio: Explicabilidade obrigatória.
        """
        assert len(cat.what_it_validates) > 20, (
            f"Categoria '{cat.id}' tem 'what_it_validates' muito curto. "
            "A explicação deve ser substantiva."
        )

    @pytest.mark.parametrize("cat", TEST_CATALOG)
    def test_category_has_why_it_matters(self, cat: TestCategory):
        """
        Garante que cada categoria explica por que importa.
        Princípio: Evidência acima de narrativa.
        """
        assert len(cat.why_it_matters) > 20, (
            f"Categoria '{cat.id}' tem 'why_it_matters' muito curto."
        )

    @pytest.mark.parametrize("cat", TEST_CATALOG)
    def test_category_has_valid_status(self, cat: TestCategory):
        """Garante que cada categoria tem um status válido."""
        valid_statuses = {"active", "planned", "partial"}
        assert cat.status in valid_statuses, (
            f"Categoria '{cat.id}' tem status inválido: '{cat.status}'. "
            f"Status válidos: {valid_statuses}"
        )

    @pytest.mark.parametrize("cat", TEST_CATALOG)
    def test_category_status_label_is_portuguese(self, cat: TestCategory):
        """Garante que o label de status está em português."""
        valid_labels = {"Ativo", "Planejado", "Parcial"}
        assert cat.status_label in valid_labels

    @pytest.mark.parametrize("cat", TEST_CATALOG)
    def test_category_status_css_class_is_valid(self, cat: TestCategory):
        """Garante que a classe CSS de status é válida."""
        valid_classes = {"status-active", "status-planned", "status-partial"}
        assert cat.status_css_class in valid_classes


class TestGetCategory:
    """Testes para a função get_category."""

    def test_returns_category_for_known_id(self):
        """Garante que get_category retorna a categoria correta para ID conhecido."""
        cat = get_category("domain_models")
        assert cat is not None
        assert cat.id == "domain_models"
        assert cat.title == "Domain Models"

    def test_returns_none_for_unknown_id(self):
        """Garante que get_category retorna None para ID desconhecido."""
        result = get_category("categoria_que_nao_existe_xyz")
        assert result is None

    def test_api_and_cli_has_examples(self):
        """
        Garante que a categoria 'api_and_cli' tem exemplos de testes definidos,
        pois é a categoria ativa nesta fase.
        """
        cat = get_category("api_and_cli")
        assert cat is not None
        assert len(cat.examples) > 0

    def test_active_categories_have_examples(self):
        """Garante que categorias com status 'active' têm pelo menos um exemplo."""
        catalog = get_catalog()
        active_cats = [c for c in catalog if c.status == "active"]
        for cat in active_cats:
            assert len(cat.examples) > 0, (
                f"Categoria ativa '{cat.id}' não tem exemplos de testes. "
                "Categorias ativas devem documentar exemplos concretos."
            )
