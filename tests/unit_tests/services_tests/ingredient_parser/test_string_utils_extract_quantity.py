import pytest
from mealie.services.parser_services.parser_utils.string_utils import extract_quantity_from_string

@pytest.mark.parametrize(
    "source_str, expected_qty, expected_rem",
    [
        pytest.param("", 0, "", id="P1: String vazia"),
        pytest.param("   ", 0, "", id="P1: Somente espaços"),
        pytest.param("2 cups of flour", 2.0, "cups of flour", id="P2: Inteiro simples"),
        pytest.param("1.5 cups of sugar", 1.5, "cups of sugar", id="P3: Decimal"),
        pytest.param("1/2 cup of milk", 0.5, "cup of milk", id="P4: Fração simples"),
        pytest.param("1 1/2 cups of water", 1.5, "cups of water", id="P5: Fração mista"),
        pytest.param("cups of flour", 0, "cups of flour", id="P6: String sem número"),
        pytest.param("½ cup", 0.5, "cup", id="P7: Fração vulgar Unicode"),
        pytest.param("1½ cups", 1.5, "cups", id="P8: Fração vulgar mista com inteiro"),
        pytest.param("1/0 cups", 0, "1/0 cups", id="P9: Fração com denominador zero (ZeroDivisionError)"),
        pytest.param("  3 tablespoons  ", 3.0, "tablespoons", id="P10: String com espaços extras"),
    ]
)
def test_equivalence_partitioning(source_str, expected_qty, expected_rem):
    """Garante que pelo menos um representante de cada classe de equivalência seja testado."""
    quantity, remaining = extract_quantity_from_string(source_str)
    assert quantity == pytest.approx(expected_qty)
    assert remaining == expected_rem


@pytest.mark.parametrize(
    "source_str, expected_qty, expected_rem",
    [
        pytest.param("", 0, "", id="VL1: Limite inferior absoluto"),
        pytest.param(" ", 0, "", id="VL2: Limite com um único espaço"),
        pytest.param("0 cups", 0.0, "cups", id="VL3: Limite inferior de número válido (zero)"),
        pytest.param("1 cup", 1.0, "cup", id="VL4: Menor inteiro positivo (1)"),
        pytest.param("1/1 cup", 1.0, "cup", id="VL5: Fração com numerador == denominador"),
        pytest.param("1.0 cup", 1.0, "cup", id="VL6: Decimal com fração zero"),
        pytest.param("1 1/99 cups", 1 + 1/99, "cups", id="VL7: Fração mista com parte fracionária muito pequena"),
        pytest.param("about 2 cups", 2.0, "about  cups", id="VL8: Número no meio da string"),
        pytest.param("cups 2", 2.0, "cups", id="VL9: Número no final da string"),
        pytest.param("99999 grams", 99999.0, "grams", id="VL10: Número muito grande (limite superior)"),
    ]
)
def test_boundary_value_analysis(source_str, expected_qty, expected_rem):
    """Foca nos limites entre as partições de equivalência do domínio de entrada."""
    quantity, remaining = extract_quantity_from_string(source_str)
    assert quantity == pytest.approx(expected_qty)
    assert remaining == expected_rem


@pytest.mark.parametrize(
    "source_str, expected_qty, expected_rem",
    [
        pytest.param("   ", 0, "", id="D1-True: source_str vazia após strip"),
        pytest.param("5 grams", 5.0, "grams", id="D1-False: source_str NÃO é vazia após strip"),
        pytest.param("2 3/4 teaspoons", 2.75, "teaspoons", id="D2-True: Match em mixed_fraction_pattern"),
        pytest.param("3/4 cup", 0.75, "cup", id="D2-False, D3-True: Match em fraction_pattern"),
        pytest.param("10 grams", 10.0, "grams", id="D2-False, D3-False, D4-True: Match em number_pattern"),
        pytest.param("just flour", 0, "just flour", id="D2, D3, D4-False: Nenhum match encontrado"),
        pytest.param("3/0 tablespoons", 0, "3/0 tablespoons", id="D5: ZeroDivisionError capturado"),
    ]
)
def test_branch_coverage(source_str, expected_qty, expected_rem):
    """Assegura que as 5 decisões (D1-D5) do fluxo de controle sejam exercitadas como True e False."""
    quantity, remaining = extract_quantity_from_string(source_str)
    assert quantity == pytest.approx(expected_qty)
    assert remaining == expected_rem


@pytest.mark.parametrize(
    "source_str, expected_qty, expected_rem",
    [
        pytest.param("2 1/3 cups", 2 + 1/3, "cups", id="T1: A=True (fração mista) determina o resultado"),
        pytest.param("2/3 cups", 2/3, "cups", id="T2: A=False, B=True (fração simples) determina o resultado"),
        pytest.param("42 grams", 42.0, "grams", id="T3: A=False, B=False, C=True (número) determina o resultado"),
        pytest.param("salt and pepper", 0, "salt and pepper", id="T4: Todas as condições False acionam o fallback"),
    ]
)
def test_mcdc_coverage(source_str, expected_qty, expected_rem):
    """
    Condições do try-block modeladas como A (mista), B (fração) e C (número).
    Garante que cada condição individualmente altera o fluxo de decisão.
    """
    quantity, remaining = extract_quantity_from_string(source_str)
    assert quantity == pytest.approx(expected_qty)
    assert remaining == expected_rem


@pytest.mark.parametrize(
    "source_str, expected_qty, expected_rem",
    [
        pytest.param("1-2 cups", 1.5, "cups", id="R1: Range com hífen"),
        pytest.param("1 to 2 cups", 1.5, "cups", id="R2: Range com 'to'"),
        pytest.param("0.5-1.5 liters", 1.0, "liters", id="R3: Range com decimais"),
    ]
)
def test_quantity_ranges(source_str, expected_qty, expected_rem):
    """Testa a extração de quantidades em formato de intervalo (range), retornando a média."""
    quantity, remaining = extract_quantity_from_string(source_str)
    assert quantity == pytest.approx(expected_qty)
    assert remaining == expected_rem

