# Testes de parse_nutrition

Os 18 casos verificam a leitura das informações nutricionais importadas do MyRecipeBox. O arquivo de testes é `tests/unit_tests/services_tests/test_myrecipebox_nutrition.py`.

## Executar

Na raiz do projeto, com Python 3.14 e uv:

```bash
uv sync --frozen --group dev --no-install-package python-ldap --no-install-project

TESTING=True PRODUCTION=True DATA_DIR=/tmp/mealie-nutrition-tests \
  uv run --no-sync python -m pytest --noconftest \
  tests/unit_tests/services_tests/test_myrecipebox_nutrition.py
```

LDAP não é usado nesses testes. A opção `--noconftest` evita carregar as fixtures globais que inicializam o banco. O limpador nutricional é substituído por um mock.

## Cobertura

```bash
TESTING=True PRODUCTION=True DATA_DIR=/tmp/mealie-nutrition-tests \
  uv run --no-sync python -m coverage run --branch \
  --data-file=/tmp/mealie-nutrition.coverage \
  --source=mealie.services.migrations.myrecipebox \
  -m pytest --noconftest \
  tests/unit_tests/services_tests/test_myrecipebox_nutrition.py

uv run --no-sync python -m coverage html \
  --data-file=/tmp/mealie-nutrition.coverage \
  -d docs/testes-nutricao/cobertura
```

Abra [cobertura/index.html](cobertura/index.html) no navegador. Na aba **functions**, procure `MyRecipeBoxMigrator.parse_nutrition`.

Os 18 testes passaram, cobrindo 14/14 linhas e 6/6 ramos do corpo desse método. O relatório também mostra outros métodos do arquivo, que não fazem parte destes testes. As tabelas de equivalência, valores-limite e pares MC/DC estão no relatório entregue no Aprender.
