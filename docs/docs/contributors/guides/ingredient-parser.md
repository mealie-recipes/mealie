# Improving the Ingredient Parser

Mealie has three ingredient parsers. The user selects one in the ingredient parser dialog.

| Parser | Value | Code |
|--------|-------|------|
| Natural Language Processor | `nlp` | `NLPParser` in `mealie/services/parser_services/ingredient_parser.py` |
| Brute Parser | `brute` | `BruteForceParser` in the same file, and `mealie/services/parser_services/brute/` |
| AI Parser | `openai` | `mealie/services/parser_services/openai/`. The UI shows it only when the group has an [AI provider](../../documentation/getting-started/installation/ai-providers.md). |

The UI selects the Natural Language Processor by default for English, and the Brute Parser for other languages.

All parsers extend `ABCIngredientParser` in `mealie/services/parser_services/_base.py`. After a parser reads an ingredient, it calls `find_ingredient_match` from the base class. This method matches the food and the unit to the foods and units of the group.

## The Natural Language Processor

The Natural Language Processor uses the [ingredient-parser](https://github.com/strangetom/ingredient-parser) Python package (`ingredient-parser-nlp` in `pyproject.toml`). The package contains the trained model, so Mealie does not train or download a model. The model is trained on English recipes.

`NLPParser` does these steps:

1. It gives the names and abbreviations of the group's units to the package as custom units.
2. It uses the first amount as the quantity and the unit.
3. It puts the size, preparation, comment, and purpose into the note. It puts other amounts at the start of the note.
4. It changes alternative ingredients (for example "stock or broth") into substitutions.

If the package reads an ingredient sentence incorrectly, report the problem to the [ingredient-parser project](https://github.com/strangetom/ingredient-parser/issues). If Mealie changes a correct result into an incorrect one, change `NLPParser` in Mealie.

## Testing

The parser tests are in `tests/unit_tests/services_tests/ingredient_parser/`. Each parser has a test file. These tests run in CI with the other tests.

Add a test case for each problem that you fix. To run only the parser tests:

```bash
mise run py:test -- tests/unit_tests/services_tests/ingredient_parser
```

In your PR, give the ingredient sentences, the result before your change, and the result after your change.

## Alternative Parsers

To add a parser:

1. Make a class that extends `ABCIngredientParser` and implements `parse_one` and `parse`.
2. Add a value to the `RegisteredParser` enum in `mealie/schema/recipe/recipe_ingredient.py`.
3. Add the class to `__registrar` in `mealie/services/parser_services/ingredient_parser.py`. `get_parser` uses this dictionary.
4. Run `mise run dev:generate` to update the TypeScript types.
5. Add the parser to `availableParsers` in `frontend/app/composables/recipes/use-parse-ingredients-dialog.ts`. Add its label to `frontend/app/lang/messages/en-US.json`.

## Links

- [ingredient-parser on GitHub](https://github.com/strangetom/ingredient-parser)
- [ingredient-parser documentation](https://ingredient-parser.readthedocs.io/en/latest/)
