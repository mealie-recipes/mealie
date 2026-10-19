# Unit testy czarnoskrzynkowe — KacperS

**Obszar:** bezpieczeństwo i walidacja danych
**Pliki źródłowe:**
- `mealie/core/security/hasher.py`
- `mealie/core/security/tokens.py`
- `mealie/core/security/security.py`
- `mealie/pkgs/safehttp/transport.py`
- `mealie/schema/recipe/recipe.py`
- `mealie/schema/_mealie/datetime_parse.py`
- `mealie/schema/_mealie/validators.py`
- `mealie/pkgs/stats/fs_stats.py`
- `mealie/services/migrations/utils/migration_helpers.py`

**Plik z testami:** `tests/black_box/test_KacperS.py`

## Funkcje do przetestowania (10)

| # | Funkcja | Plik | Opis |
|---|---|---|---|
| 1 | `Hasher.hash(password: str) -> str` (przez `get_hasher()`) | `hasher.py` | Hashuje hasło |
| 2 | `Hasher.verify(password: str, hashed: str) -> bool` | `hasher.py` | Sprawdza hasło z hashem |
| 3 | `create_access_token(data: dict, expires_delta: timedelta \| None = None) -> tuple[str, timedelta]` | `tokens.py` | Tworzy token JWT i zwraca jego czas ważności |
| 4 | `url_safe_token() -> str` | `security.py` | Generuje losowy token bezpieczny do użycia w URL |
| 5 | `is_blocked_ip(ip) -> bool` | `transport.py` | Czy połączenie z danym IP powinno być zablokowane (ochrona przed SSRF) |
| 6 | `create_recipe_slug(name: str, max_length: int = 250) -> str` | `recipe.py` | Tworzy slug (fragment URL) z nazwy przepisu |
| 7 | `parse_date(value: date \| str \| bytes \| int \| float) -> date` | `datetime_parse.py` | Parsuje datę z różnych formatów |
| 8 | `pretty_size(size: int) -> str` | `fs_stats.py` | Zamienia rozmiar w bajtach na czytelny tekst |
| 9 | `safe_local_path(candidate: str \| Path, root: Path) -> Path \| None` | `migration_helpers.py` | Zwraca ścieżkę tylko jeśli leży wewnątrz `root` (ochrona przed `../`) |
| 10 | `validate_locale(locale: str) -> bool` | `validators.py` | Sprawdza, czy kod języka jest poprawny |

## Co zrobić

1. **Zasada czarnej skrzynki:** przypadki testowe projektujemy **tylko na podstawie sygnatury, nazwy i docstringa** funkcji. Nie czytamy kodu w środku funkcji. Nie kopiujemy istniejących testów z `tests/unit_tests/`.
2. Dla każdej funkcji przygotuj **min. 3–5 przypadków testowych**, w tym:
   - poprawne dane wejściowe (typowe użycie),
   - przypadki brzegowe (pusty string, 0, bardzo długa nazwa vs `max_length`, granice jednostek w `pretty_size`),
   - niepoprawne / złośliwe dane (złe hasło, `127.0.0.1` / `192.168.x.x` / `::1`, ścieżki z `../`, nieistniejący locale, polskie znaki w nazwie przepisu).
3. Przy funkcjach losowych (`url_safe_token`, `hash`) testuj **właściwości** wyniku, a nie konkretną wartość (np. długość, dozwolone znaki, dwa wywołania dają różne wyniki, `verify(hash(x))` zwraca `True`).
4. Wpisz przypadki do tabeli w sekcji **Przypadki testowe** poniżej (to jest część dokumentacji oddawanej prowadzącej).
5. Zaimplementuj testy w `tests/black_box/test_KacperS.py` w `pytest` (najlepiej `@pytest.mark.parametrize`, ID przypadku jako `id=`). Do `safe_local_path` użyj fixture `tmp_path`.
6. Uruchom testy: `uv run pytest tests/black_box/test_KacperS.py -v`
7. Jeśli test nie przechodzi — **nie poprawiaj go „pod kod”**. Zapisz w kolumnie *Wynik* `FAIL` i krótko opisz rozbieżność (to też jest wartościowy wynik testów).
8. Zrób własny branch (np. `tests/KacperS`) i PR do `mealie-next`.

## Przypadki testowe

| ID | Funkcja | Opis przypadku | Wejście | Oczekiwane wyjście | Typ | Wynik |
|---|---|---|---|---|---|---|
| KS-01 | `Hasher.verify` | _przykład:_ poprawne hasło pasuje do swojego hasha | `("haslo123", hash("haslo123"))` | `True` | poprawny | |
| KS-02 | | | | | | |
