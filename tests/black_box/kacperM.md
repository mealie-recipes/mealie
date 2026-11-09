# Unit testy czarnoskrzynkowe — KacperM

**Funkcjonalność:** import przepisu z adresu URL
**Plik źródłowy:** `mealie/services/scraper/cleaner.py`
**Pliki z testami:** `tests/black_box/kacper/`

Użytkownik wkleja link do przepisu, a Mealie pobiera dane ze strony i zamienia je na przepis. Dane ze stron przychodzą w bardzo różnych formatach (string, lista, słownik, puste wartości), więc te funkcje muszą je ujednolicić.

## Testowane funkcje (3)

| # | Funkcja | Za co odpowiada w przepisie | Plik z testami |
|---|---|---|---|
| 1 | `clean_ingredients(ingredients: list \| str \| None, default: list \| None = None) -> list[str \| dict]` | Lista składników | `test_clean_ingredients.py` |
| 2 | `clean_duration(time_entry: Any) -> int \| None` | Czas przygotowania | `test_clean_duration.py` |
| 3 | `clean_image(image: str \| list \| dict \| None = None, default: str = NO_IMAGE) -> list[str]` | Zdjęcie przepisu | `test_clean_image.py` |

## Metoda

Przypadki zaprojektowano wyłącznie na podstawie specyfikacji funkcji: sygnatury (typy parametrów i wyniku) oraz docstringa. Implementacji nie analizowano. Wejścia podzielono na klasy równoważności:

- **poprawny**: format wymieniony w specyfikacji jako obsługiwany,
- **brzegowy**: puste wartości (`None`, `""`, `[]`, `{}`), zero, wartości ujemne i zbyt duże, użycie parametru `default`,
- **nietypowy**: obsługiwany, ale rzadszy format (np. słownik zamiast listy),
- **niepoprawny**: typ lub struktura, których specyfikacja nie obsługuje (oczekiwany `TypeError`, bo docstring go zapowiada).

W kolumnie *Wynik* przy `FAIL` podano faktyczne zachowanie funkcji, różne od oczekiwanego.

Testy zaimplementowano w `pytest` (`@pytest.mark.parametrize`, ID przypadku jako `id=`).

## Uruchomienie

Z aktywnym środowiskiem projektu (`.venv\Scripts\Activate.ps1`):

```powershell
python -m pytest tests/black_box/kacper -v                              # wszystkie zbiory
python -m pytest tests/black_box/kacper/test_clean_image.py -v          # jeden zbiór
```

## Przypadki testowe

### 1. `clean_ingredients`

Specyfikacja (z docstringa): funkcja przyjmuje listę stringów, pojedynczy string albo `None` i zwraca listę składników. `None` daje pustą listę. Dla nieobsługiwanego typu zgłaszany jest `TypeError`. Przypadki wynikają z tej specyfikacji i z nazw parametrów (`default`).

| ID | Opis przypadku | Wejście | Oczekiwane wyjście | Typ | Wynik |
|---|---|---|---|---|---|
| KM-01 | Lista kilku składników | `["1 cup flour", "2 eggs"]` | `["1 cup flour", "2 eggs"]` | poprawny | PASS |
| KM-02 | Pojedynczy składnik jako string | `"1 cup flour"` | `["1 cup flour"]` | poprawny | PASS |
| KM-03 | Brak składników | `None` | `[]` | brzegowy | PASS |
| KM-04 | Brak składników, podana wartość domyślna | `None`, `default=["1 egg"]` | `["1 egg"]` | brzegowy | PASS |
| KM-05 | Brak składników, pusta wartość domyślna | `None`, `default=[]` | `[]` | brzegowy | PASS |
| KM-06 | Pusta lista | `[]` | `[]` | brzegowy | PASS |
| KM-07 | Powtórzony składnik (zachowanie duplikatów) | `["1 egg", "1 egg"]` | `["1 egg", "1 egg"]` | poprawny | PASS |
| KM-08 | Nieobsługiwany typ: liczba | `123` | `TypeError` | niepoprawny | PASS |
| KM-09 | Nieobsługiwany typ: słownik | `{"name": "flour"}` | `TypeError` | niepoprawny | PASS |
| KM-10 | Nieobsługiwany typ: krotka | `("1 egg",)` | `TypeError` | niepoprawny | FAIL: funkcja nie zgłasza `TypeError`, tylko zwraca `["1 egg"]`. |

### 2. `clean_duration`

Specyfikacja (z docstringa): funkcja zamienia czas przygotowania na liczbę sekund. Przyjmuje czas w formacie ISO 8601 (`"PT1H30M"`), liczbę lub string z liczbą (traktowane jako minuty), `timedelta`, słownik `{"minValue": ...}` albo listę (bierze pierwszą wartość). Czas, który nie jest dodatni albo nie mieści się w bazie danych, daje `None`. Każde inne wejście (np. zwykły tekst) też daje `None`.

| ID | Opis przypadku | Wejście | Oczekiwane wyjście | Typ | Wynik |
|---|---|---|---|---|---|
| KM-11 | Czas w formacie ISO 8601 | `"PT1H30M"` | `5400` | poprawny | PASS |
| KM-12 | Liczba minut | `30` | `1800` | poprawny | PASS |
| KM-13 | Liczba minut jako string | `"30"` | `1800` | poprawny | PASS |
| KM-14 | Obiekt `timedelta` | `timedelta(hours=1)` | `3600` | poprawny | PASS |
| KM-15 | Słownik z kluczem `minValue` | `{"minValue": "PT1H"}` | `3600` | nietypowy | PASS |
| KM-16 | Lista czasów (brana pierwsza wartość) | `["PT1H", "PT2H"]` | `3600` | nietypowy | PASS |
| KM-17 | Brak czasu | `None` | `None` | brzegowy | PASS |
| KM-18 | Pusty string | `""` | `None` | brzegowy | PASS |
| KM-19 | Pusta lista | `[]` | `None` | brzegowy | PASS |
| KM-20 | Zero minut | `0` | `None` | brzegowy | PASS |
| KM-21 | Ujemna liczba minut | `-5` | `None` | brzegowy | PASS |
| KM-22 | Zerowy czas w formacie ISO 8601 | `"PT0S"` | `None` | brzegowy | PASS |
| KM-23 | Zwykły tekst zamiast czasu | `"about 20 minutes"` | `None` | nietypowy | PASS |
| KM-24 | Czas za długi dla bazy danych | `10**12` | `None` | brzegowy | PASS |

### 3. `clean_image`

Specyfikacja (z docstringa): funkcja przyjmuje adres zdjęcia jako string, słownik z kluczem `url`, listę stringów albo listę słowników z kluczem `url` i zwraca listę adresów. Puste wejście daje `[default]` (domyślnie `NO_IMAGE` = `"no image"`). Dla nieobsługiwanego typu zgłaszany jest `TypeError`.

Oznaczenia w tabeli: `URL` = `"https://example.com/a.jpg"`, `URL_2` = `"https://example.com/b.jpg"`.

| ID | Opis przypadku | Wejście | Oczekiwane wyjście | Typ | Wynik |
|---|---|---|---|---|---|
| KM-25 | Adres zdjęcia jako string | `URL` | `[URL]` | poprawny | PASS |
| KM-26 | Słownik z kluczem `url` | `{"url": URL}` | `[URL]` | poprawny | PASS |
| KM-27 | Lista adresów | `[URL, URL_2]` | `[URL, URL_2]` | poprawny | PASS |
| KM-28 | Lista słowników z kluczem `url` | `[{"url": URL}, {"url": URL_2}]` | `[URL, URL_2]` | poprawny | PASS |
| KM-29 | Brak zdjęcia | `None` | `["no image"]` | brzegowy | PASS |
| KM-30 | Pusty string | `""` | `["no image"]` | brzegowy | PASS |
| KM-31 | Pusta lista | `[]` | `["no image"]` | brzegowy | PASS |
| KM-32 | Pusty słownik | `{}` | `["no image"]` | brzegowy | PASS |
| KM-33 | Brak zdjęcia, podana wartość domyślna | `None`, `default=URL_2` | `[URL_2]` | brzegowy | PASS |
| KM-34 | Nieobsługiwany typ: liczba | `123` | `TypeError` | niepoprawny | FAIL: funkcja nie zgłasza `TypeError`, tylko zwraca `["no image"]`. |
| KM-35 | Nieobsługiwana struktura: słownik bez klucza `url` | `{"src": URL}` | `TypeError` | niepoprawny | FAIL: funkcja nie zgłasza `TypeError`, tylko zwraca `["no image"]`. |
| KM-36 | Nieobsługiwany typ: lista liczb | `[1, 2]` | `TypeError` | niepoprawny | FAIL: funkcja nie zgłasza `TypeError`, tylko zwraca `["no image"]`. |

## Podsumowanie wyników

| Funkcja | Przypadki | PASS | FAIL |
|---|---|---|---|
| `clean_ingredients` | 10 | 9 | 1 (KM-10) |
| `clean_duration` | 14 | 14 | 0 |
| `clean_image` | 12 | 9 | 3 (KM-34–KM-36) |
| **Razem** | **36** | **32** | **4** |

## Wnioski

- Wszystkie wykryte rozbieżności dotyczą obsługi nieobsługiwanych typów: docstring zapowiada `TypeError`, a funkcja zamiast tego zwraca wartość.
- Dla poprawnych i pustych danych wejściowych funkcje działają zgodnie ze specyfikacją.

## Analiza pokrycia kodu

Testy uruchamiają się bez poprawek (32 PASS, 4 FAIL, przy czym FAIL to wykryte rozbieżności ze specyfikacją, a nie błędy uruchomienia). Pokrycie zmierzono narzędziem coverage.py 7.16.2 z pomiarem pokrycia gałęzi:

```powershell
python -m coverage run --branch --include="*cleaner.py" -m pytest tests/black_box/kacper
python -m coverage html
```

### Osiągnięte pokrycie

| Funkcja | Instrukcje | Niewykonane | Pokrycie instrukcji | Gałęzie | Częściowe | Pokrycie gałęzi | Pokrycie łączne |
|---|---|---|---|---|---|---|---|
| `clean_ingredients` | 16 | 1 | 94% | 12 | 1 | 92% | **93%** |
| `clean_duration` | 23 | 1 | 96% | 18 | 1 | 94% | **95%** |
| `clean_image` | 16 | 1 | 94% | 12 | 1 | 92% | **93%** |

Funkcje pomocnicze, wywoływane przez testowane funkcje, zostały wykonane pośrednio: `parse_duration` (wywoływana przez `clean_duration`) w 100%, `clean_string` (wywoływana przez `clean_ingredients`) w 41%. Pokrycie całego pliku `cleaner.py` wynosi 28%, ponieważ zawiera on funkcje, które nie były przedmiotem testów (np. `clean_instructions`, `clean_yield`, `clean_nutrition`).

### Przypadek o największym pokryciu

Każdy przypadek uruchomiono osobno z pomiarem pokrycia (`coverage run ... pytest "<id przypadku>"`) i odczytano pokrycie łączne testowanej funkcji.

| Funkcja | Przypadek o największym pokryciu | Pokrycie | Najmniejsze pokrycie |
|---|---|---|---|
| `clean_ingredients` | KM-01, KM-07 (lista stringów) | 46,4% | KM-03, KM-04, KM-05 (`None`): 14,3% |
| `clean_duration` | KM-16 (lista czasów `["PT1H", "PT2H"]`) | 58,5% | KM-12, KM-20, KM-21, KM-24 (liczby): 22,0% |
| `clean_image` | KM-34, KM-35, KM-36 (nieobsługiwane typy) | 57,1% | KM-29–KM-33 (puste wejście): 10,7% |

Pełne wyniki:

| Przypadek | Pokrycie | Przypadek | Pokrycie | Przypadek | Pokrycie |
|---|---|---|---|---|---|
| KM-01 | 46,4% | KM-13 | 34,1% | KM-25 | 21,4% |
| KM-02 | 35,7% | KM-14 | 31,7% | KM-26 | 42,9% |
| KM-03 | 14,3% | KM-15 | 53,7% | KM-27 | 28,6% |
| KM-04 | 14,3% | KM-16 | 58,5% | KM-28 | 35,7% |
| KM-05 | 14,3% | KM-17 | 36,6% | KM-29 | 10,7% |
| KM-06 | 32,1% | KM-18 | 31,7% | KM-30 | 10,7% |
| KM-07 | 46,4% | KM-19 | 36,6% | KM-31 | 10,7% |
| KM-08 | 39,3% | KM-20 | 22,0% | KM-32 | 10,7% |
| KM-09 | 39,3% | KM-21 | 22,0% | KM-33 | 10,7% |
| KM-10 | 28,6% | KM-22 | 39,0% | KM-34 | 57,1% |
| KM-11 | 39,0% | KM-23 | 31,7% | KM-35 | 57,1% |
| KM-12 | 22,0% | KM-24 | 22,0% | KM-36 | 57,1% |

- `clean_duration`: KM-16 i KM-15 dają najwięcej, bo funkcja wywołuje się rekurencyjnie: najpierw obsługuje listę albo słownik, a potem jeszcze raz przetwarza wyciągniętą wartość jako string w formacie ISO 8601.
- `clean_image`: nieobsługiwany typ nie pasuje do żadnego wzorca, więc funkcja sprawdza kolejno wszystkie warunki, zanim dojdzie do przypadku domyślnego.
- `clean_ingredients`: lista stringów przechodzi przez pętlę po elementach i czyszczenie każdego z nich.
- Puste wejście daje najmniejsze pokrycie, bo funkcja kończy działanie na pierwszym warunku.

### Niewykonane linie i brakujące przypadki testowe

Numery linii odnoszą się do pliku `mealie/services/scraper/cleaner.py` w tej gałęzi (z dopisanymi komentarzami).

| Funkcja | Linia | Niewykonany fragment | Przypadek, który by go pokrył |
|---|---|---|---|
| `clean_ingredients` | 364 | obsługa słownika jako elementu listy (warunek w linii 363 nigdy nie był prawdziwy) | lista zawierająca słownik, np. `[{"name": "flour"}]` |
| `clean_duration` | 496 | zwrócenie `None` dla wartości logicznej (gałąź `case bool()` w linii 495) | wartość `True` lub `False` |
| `clean_image` | 151 | obsługa listy słowników z kluczem `@id` (gałąź w linii 150) | lista słowników z kluczem `@id`, np. `[{"@id": URL}]` |

### Wnioski

- Testy czarnoskrzynkowe osiągnęły wysokie pokrycie testowanych funkcji (93–95%), mimo że projektowano je bez znajomości kodu.
- Żaden pojedynczy przypadek nie przekracza 60% pokrycia swojej funkcji. Wysokie pokrycie daje dopiero zestaw przypadków z różnych klas równoważności, co potwierdza sens podziału wejść na klasy.
- Największe pokrycie dają przypadki, które przechodzą przez wiele warunków: dane zagnieżdżone (rekurencja w `clean_duration`) oraz nieobsługiwane typy (`clean_image`). Te drugie wykryły jednocześnie niezgodność ze specyfikacją.
- Wszystkie trzy niewykonane fragmenty obsługują dane, których specyfikacja (docstring) nie wymienia: słownik w liście składników, wartość logiczna jako czas i klucz `@id` w zdjęciu. Testy oparte na specyfikacji nie mogły na nie trafić, więc niepełne pokrycie wynika z niepełnej dokumentacji, a nie z pominięcia klasy równoważności.
- Wysokie pokrycie nie oznacza braku błędów. Przypadki KM-10 i KM-34–KM-36 wykonują kod funkcji, a mimo to wykazały niezgodność zachowania ze specyfikacją. Pokrycie mówi, które linie się wykonały, a nie czy wynik był poprawny.
- Analiza pokrycia uzupełnia testy czarnoskrzynkowe: wskazuje zachowania istniejące w kodzie, ale nieopisane w specyfikacji, które warto udokumentować i przetestować.
