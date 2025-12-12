# Instrukcja dla Claude

Ten plik definiuje workflow pracy w projekcie. Przeczytaj przed każdą zmianą w kodzie.

## Workflow - ZAWSZE stosuj tę kolejność

```
1. TEST   → Napisz test w tests/ dla nowej funkcjonalności
2. FAIL   → Uruchom: pytest tests/test_<nazwa>.py -v (musi FAILOWAĆ)
3. CODE   → Napisz minimalną implementację w src/
4. PASS   → Uruchom: pytest tests/test_<nazwa>.py -v (musi PRZECHODZIĆ)
5. ALL    → Uruchom: pytest (wszystkie testy muszą przechodzić)
6. DOCS   → Zaktualizuj README.md i CLAUDE.md jeśli potrzeba
```

**NIGDY nie pisz kodu bez testu najpierw.**

## Struktura projektu

```
config/settings.py      → Konfiguracja (env, paths, headers)
src/scrapers/base.py    → BaseScraper ABC - dziedzicz z tej klasy
src/scrapers/           → Implementacje scraperów
src/models/             → Modele Pydantic
src/pipelines/          → Pipeline'y przetwarzania danych
src/utils/              → Narzędzia (logger, export)
tests/                  → Testy jednostkowe
zadania/                → Zadania do realizacji
```

## Styl kodu

### Docstringi Google - WYMAGANE dla każdej funkcji/klasy

```python
def nazwa_funkcji(arg1: str, arg2: int = 10) -> dict:
    """Krótki opis co robi funkcja.

    Dłuższy opis jeśli potrzebny.

    Args:
        arg1: Opis argumentu.
        arg2: Opis z domyślną wartością.

    Returns:
        Opis co zwraca.

    Raises:
        NazwaWyjatku: Kiedy występuje.
    """
```

### Nazewnictwo

- `snake_case` → zmienne, funkcje
- `PascalCase` → klasy
- `UPPER_SNAKE_CASE` → stałe
- `_prefix` → metody prywatne

### Struktura pliku

```python
"""Docstring modułu."""

# Importy standardowe
import json

# Importy zewnętrzne
import requests

# Importy lokalne
from config.settings import X

# Stałe
MAX_VALUE = 100

# Klasy i funkcje
```

### Zasady

- Maksymalna długość linii: 88 znaków
- Type hints dla wszystkich argumentów i zwracanych wartości
- Jedna funkcja = jedno zadanie
- Maksymalnie 3 poziomy zagnieżdżenia
- Nie używaj magic numbers - definiuj stałe

## Testy

### Struktura testu (Arrange-Act-Assert)

```python
def test_parse_extracts_title(self):
    """Opis co testujemy."""
    # Arrange
    scraper = MyScraper()
    html = "<h1>Title</h1>"

    # Act
    result = scraper.parse(html)

    # Assert
    assert result["title"] == "Title"
```

### Nazewnictwo testów

```
test_<metoda>_<scenariusz>_<oczekiwany_rezultat>

test_parse_with_valid_html_returns_dict
test_fetch_when_timeout_raises_exception
```

## Komendy

```bash
pytest                           # Wszystkie testy
pytest tests/test_x.py -v        # Konkretny plik
pytest -k "test_parse"           # Testy zawierające "test_parse"
source venv/bin/activate         # Aktywacja venv
```

## Checklist przed zakończeniem zadania

- [ ] Testy napisane PRZED kodem
- [ ] Wszystkie testy przechodzą (`pytest`)
- [ ] Docstringi Google dla nowych funkcji/klas
- [ ] Type hints dodane
- [ ] README.md zaktualizowany (jeśli nowa funkcjonalność)
- [ ] CLAUDE.md zaktualizowany (jeśli zmiana workflow)

## Aktualny stan projektu

### Zaimplementowane
- BaseScraper (klasa abstrakcyjna)
- DataPipeline (łańcuch procesorów)
- Export do JSON/CSV
- Logger z rotacją

### Do zaimplementowania
- (uzupełniaj na bieżąco)
