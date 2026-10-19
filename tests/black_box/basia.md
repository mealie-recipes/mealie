# Unit testy czarnoskrzynkowe — Basia

**Obszar:** parsowanie składników i przeliczanie jednostek
**Pliki źródłowe:**
- `mealie/services/parser_services/brute/process.py`
- `mealie/services/parser_services/parser_utils/string_utils.py`
- `mealie/services/parser_services/parser_utils/unit_utils.py`
- `mealie/schema/recipe/recipe_ingredient.py`

**Plik z testami:** `tests/black_box/test_basia.py`

## Funkcje do przetestowania (10)

| # | Funkcja | Plik | Opis |
|---|---|---|---|
| 1 | `parse_fraction(x)` | `brute/process.py` | Zamienia ułamek zapisany tekstem na liczbę |
| 2 | `parse_amount(ing_str) -> tuple[float, str, str]` | `brute/process.py` | Wyciąga ilość i jednostkę z tekstu składnika |
| 3 | `move_parens_to_end(ing_str) -> str` | `string_utils.py` | Przenosi tekst w nawiasach na koniec stringa |
| 4 | `remove_footnote_markers(ing_str: str) -> str` | `string_utils.py` | Usuwa znaczniki przypisów |
| 5 | `convert_vulgar_fractions_to_regular_fractions(text: str) -> str` | `string_utils.py` | Zamienia znaki typu `½` na `1/2` |
| 6 | `extract_quantity_from_string(source_str: str) -> tuple[float, str]` | `string_utils.py` | Wyciąga ilość z początku tekstu |
| 7 | `UnitConverter.can_convert(unit, to_unit) -> bool` | `unit_utils.py` | Czy da się przeliczyć jedną jednostkę na drugą |
| 8 | `UnitConverter.convert(quantity: float, unit, to_unit) -> tuple[float, Unit]` | `unit_utils.py` | Przelicza ilość na inną jednostkę |
| 9 | `UnitConverter.merge(quantity_1, unit_1, quantity_2, unit_2) -> tuple[float, Unit]` | `unit_utils.py` | Sumuje dwie ilości w (różnych) jednostkach |
| 10 | `display_fraction(fraction: Fraction)` | `recipe_ingredient.py` | Formatuje ułamek do wyświetlenia |

## Co zrobić

1. **Zasada czarnej skrzynki:** przypadki testowe projektujemy **tylko na podstawie sygnatury, nazwy i docstringa** funkcji. Nie czytamy kodu w środku funkcji. Nie kopiujemy istniejących testów z `tests/unit_tests/`.
2. Dla każdej funkcji przygotuj **min. 3–5 przypadków testowych**, w tym:
   - poprawne dane wejściowe (typowe użycie),
   - przypadki brzegowe (0, ułamki niewłaściwe typu `3/2`, liczby mieszane typu `1 1/2`, pusty string),
   - niepoprawne / nietypowe dane (nieznana jednostka, jednostki nieprzeliczalne np. gram → litr, dzielenie przez zero `1/0`).
3. Wpisz przypadki do tabeli w sekcji **Przypadki testowe** poniżej (to jest część dokumentacji oddawanej prowadzącej).
4. Zaimplementuj testy w `tests/black_box/test_basia.py` w `pytest` (najlepiej `@pytest.mark.parametrize`, ID przypadku jako `id=`). Przy porównywaniu floatów używaj `pytest.approx`.
5. Uruchom testy: `uv run pytest tests/black_box/test_basia.py -v`
6. Jeśli test nie przechodzi — **nie poprawiaj go „pod kod”**. Zapisz w kolumnie *Wynik* `FAIL` i krótko opisz rozbieżność (to też jest wartościowy wynik testów).
7. Zrób własny branch (np. `tests/basia`) i PR do `mealie-next`.

## Przypadki testowe

| ID | Funkcja | Opis przypadku | Wejście | Oczekiwane wyjście | Typ | Wynik |
|---|---|---|---|---|---|---|
| B-01 | `parse_fraction` | _przykład:_ zwykły ułamek | `"1/2"` | `0.5` | poprawny | |
| B-02 | | | | | | |
