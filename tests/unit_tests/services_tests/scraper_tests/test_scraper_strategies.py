import json

from recipe_scrapers import scrape_html

from mealie.lang.providers import get_locale_provider
from mealie.services.scraper.scraper_strategies import RecipeScraperPackage, contains_how_to_section

SECTIONED_RECIPE = {
    "@context": "https://schema.org/",
    "@type": "Recipe",
    "name": "Sectioned Recipe",
    "recipeIngredient": ["1 onion", "1 lb beef"],
    "recipeInstructions": [
        {
            "@type": "HowToSection",
            "name": "Prep Work",
            "itemListElement": [
                {"@type": "HowToStep", "text": "Dice the onion."},
                {"@type": "HowToStep", "text": "Mince the garlic."},
            ],
        },
        {
            "@type": "HowToSection",
            "name": "Cooking",
            "itemListElement": [
                {"@type": "HowToStep", "text": "Brown the beef."},
            ],
        },
    ],
}

FLAT_RECIPE = {
    "@context": "https://schema.org/",
    "@type": "Recipe",
    "name": "Flat Recipe",
    "recipeIngredient": ["1 onion"],
    "recipeInstructions": [
        {"@type": "HowToStep", "text": "Dice the onion."},
        {"@type": "HowToStep", "text": "Brown the beef."},
    ],
}


def scrape(recipe_data: dict):
    """Parse a schema.org Recipe the way the html-or-json route does."""
    html = RecipeScraperPackage.ld_json_to_html(json.dumps(recipe_data))
    scraped_data = scrape_html(html, org_url="https://example.com", supported_only=False)

    strategy = RecipeScraperPackage(
        "https://example.com",
        get_locale_provider(),
        repos=None,  # type: ignore[arg-type]
    )
    recipe, _ = strategy.clean_scraper(scraped_data, "https://example.com")
    return recipe


def test_how_to_section_names_are_kept_as_step_titles():
    """Section headings must survive an import as `RecipeStep.title`.

    recipe_scrapers flattens `HowToSection` into newline separated text and emits each
    section name as a line of its own, so importing a sectioned recipe used to turn every
    heading into a bogus instruction step (mealie-recipes/mealie#6887). The structured
    data is read directly instead, and the heading is stored on the first step of its
    section, which is how the frontend groups steps.
    """
    steps = scrape(SECTIONED_RECIPE).recipe_instructions
    assert steps is not None

    assert [(step.title, step.text) for step in steps] == [
        ("Prep Work", "Dice the onion."),
        ("", "Mince the garlic."),
        ("Cooking", "Brown the beef."),
    ]


def test_section_names_are_not_imported_as_instruction_steps():
    steps = scrape(SECTIONED_RECIPE).recipe_instructions
    assert steps is not None

    assert "Prep Work" not in [step.text for step in steps]
    assert "Cooking" not in [step.text for step in steps]


def test_recipes_without_sections_are_untouched():
    """Sites without sections must keep using the scraper's own instruction parsing."""
    steps = scrape(FLAT_RECIPE).recipe_instructions
    assert steps is not None

    assert [(step.title, step.text) for step in steps] == [
        ("", "Dice the onion."),
        ("", "Brown the beef."),
    ]


def test_single_step_section_is_imported():
    """A section holding one step as a bare dict, rather than a list, is a real shape.

    rezeptwelt.de publishes recipes this way, and it used to reach the database as a
    stringified Python dict (see `tests/utils/recipe_data.py`).
    """
    recipe_data = dict(SECTIONED_RECIPE)
    recipe_data["recipeInstructions"] = {
        "@type": "HowToSection",
        "name": "Prep Work",
        "itemListElement": {"@type": "HowToStep", "text": "Dice the onion."},
    }

    steps = scrape(recipe_data).recipe_instructions
    assert steps is not None

    assert [(step.title, step.text) for step in steps] == [("Prep Work", "Dice the onion.")]


def test_unparseable_sections_fall_back_to_the_scraper(monkeypatch):
    """A section shape the cleaner cannot parse must not lose the scraper's own output."""
    html = RecipeScraperPackage.ld_json_to_html(json.dumps(FLAT_RECIPE))
    scraped_data = scrape_html(html, org_url="https://example.com", supported_only=False)
    scraped_data.schema.data["recipeInstructions"] = [{"@type": "HowToSection", "itemListElement": 12}]
    monkeypatch.setattr(scraped_data, "instructions", lambda: "Dice the onion.\nBrown the beef.")

    strategy = RecipeScraperPackage(
        "https://example.com",
        get_locale_provider(),
        repos=None,  # type: ignore[arg-type]
    )
    recipe, _ = strategy.clean_scraper(scraped_data, "https://example.com")
    steps = recipe.recipe_instructions
    assert steps is not None

    assert [step.text for step in steps] == ["Dice the onion.", "Brown the beef."]


def test_contains_how_to_section():
    assert contains_how_to_section(SECTIONED_RECIPE["recipeInstructions"]) is True
    assert contains_how_to_section({"@type": "HowToSection", "itemListElement": []}) is True
    assert contains_how_to_section({"type": "HowToSection", "itemListElement": []}) is True
    assert contains_how_to_section(FLAT_RECIPE["recipeInstructions"]) is False
    assert contains_how_to_section("Dice the onion.") is False
    assert contains_how_to_section(None) is False
