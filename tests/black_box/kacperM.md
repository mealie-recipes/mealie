# Unit testy czarnoskrzynkowe — KacperM

**Obszar:** import przepisu ze strony WWW (czyszczenie danych pobranych ze stron z przepisami)
**Plik źródłowy:** `mealie/services/scraper/cleaner.py`
**Plik z testami:** `tests/black_box/test_kacperM.py`

## Funkcje do przetestowania (10)

| # | Funkcja | Opis |
|---|---|---|
| 1 | `clean_string(text: str \| list \| int \| float) -> str` | Zamienia tekst / listę / liczbę na oczyszczony string |
| 2 | `clean_image(image: str \| list \| dict \| None = None, default: str = NO_IMAGE) -> list[str]` | Normalizuje informację o zdjęciu do listy URL-i |
| 3 | `clean_instructions(steps_object: list \| dict \| str, default: list \| None = None) -> list[dict]` | Normalizuje kroki przepisu do listy słowników |
| 4 | `clean_ingredients(ingredients: list \| str \| None, default: list \| None = None) -> list[str \| dict]` | Normalizuje listę składników |
| 5 | `clean_yield(yields: str \| list[str] \| None) -> tuple[float, float, str]` | Wyciąga liczbę porcji / ilość i tekst z opisu wydajności |
| 6 | `clean_int(val: str \| int \| None, min: int \| None = None, max: int \| None = None)` | Zamienia wartość na int ograniczony do zakresu |
| 7 | `clean_duration(time_entry: Any) -> int \| None` | Zamienia czas w różnych formatach na liczbę (minut) |
| 8 | `parse_duration(value: str) -> timedelta \| None` | Parsuje czas w formacie ISO 8601, np. `PT1H30M` |
| 9 | `clean_categories(category: str \| list) -> list[str]` | Normalizuje kategorie przepisu do listy nazw |
| 10 | `clean_nutrition(nutrition: dict \| None) -> dict[str, str]` | Normalizuje wartości odżywcze |

## Co zrobić

1. **Zasada czarnej skrzynki:** przypadki testowe projektujemy **tylko na podstawie sygnatury, nazwy i docstringa** funkcji. Nie czytamy kodu w środku funkcji. Nie kopiujemy istniejących testów z `tests/unit_tests/`.
2. Dla każdej funkcji przygotuj **min. 3–5 przypadków testowych**, w tym:
   - poprawne dane wejściowe (typowe użycie),
   - przypadki brzegowe (pusty string / lista, `None`, 0, wartości na granicy zakresu),
   - niepoprawne / nietypowe dane (zły typ, śmieciowy tekst, dziwne formaty).
3. Wpisz przypadki do tabeli w sekcji **Przypadki testowe** poniżej (to jest część dokumentacji oddawanej prowadzącej).
4. Zaimplementuj testy w `tests/black_box/test_kacperM.py` w `pytest` (najlepiej `@pytest.mark.parametrize`, ID przypadku jako `id=`).
5. Uruchom testy: `uv run pytest tests/black_box/test_kacperM.py -v`
6. Jeśli test nie przechodzi — **nie poprawiaj go „pod kod”**. Zapisz w kolumnie *Wynik* `FAIL` i krótko opisz rozbieżność (to też jest wartościowy wynik testów).
7. Zrób własny branch (np. `tests/kacperM`) i PR do `mealie-next`.

## Przypadki testowe

| ID | Funkcja | Opis przypadku | Wejście | Oczekiwane wyjście | Typ | Wynik |
|---|---|---|---|---|---|---|
| KM-01 | `clean_string` | _przykład:_ zwykły tekst ze spacjami na brzegach | `"  Zupa  "` | `"Zupa"` | poprawny | |
| KM-02 | | | | | | |
