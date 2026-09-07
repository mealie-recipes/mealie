import json

from recipe_scrapers import scrape_html

from mealie.lang.providers import get_locale_provider
from mealie.services.scraper.scraper_strategies import RecipeScraperPackage, prefer_structured_instructions

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


def test_step_summaries_are_kept():
    """`summary` is Mealie's own step heading, and pasted JSON is where it comes from.

    recipe_scrapers renders instructions as plain text, so the key is gone before the
    cleaner runs and a pasted Mealie export or AI generated recipe lost its step headings
    (mealie-recipes/mealie#6406). The structured data still has them.
    """
    recipe_data = dict(FLAT_RECIPE)
    recipe_data["recipeInstructions"] = [
        {"@type": "HowToStep", "summary": "Sear the beef", "text": "Sear for 2 minutes a side."},
        {"@type": "HowToStep", "text": "Deglaze with the wine."},
    ]

    steps = scrape(recipe_data).recipe_instructions
    assert steps is not None

    assert [(step.summary, step.text) for step in steps] == [
        ("Sear the beef", "Sear for 2 minutes a side."),
        ("", "Deglaze with the wine."),
    ]


def test_structured_data_is_ignored_when_it_would_merge_steps(monkeypatch):
    """Some sites put a whole method in one step, and only the scraper splits it up.

    rezeptwelt.de publishes an unnamed section holding a single step whose text is the entire
    method, while its own recipe_scrapers scraper reads the page and returns the steps
    separately. Preferring the structured data there would replace readable steps with one
    wall of text, so the scraper's own parsing has to win.
    """
    html = RecipeScraperPackage.ld_json_to_html(json.dumps(FLAT_RECIPE))
    scraped_data = scrape_html(html, org_url="https://example.com", supported_only=False)
    scraped_data.schema.data["recipeInstructions"] = [
        {
            "@type": "HowToSection",
            "itemListElement": [
                {"@type": "HowToStep", "name": "Salad", "text": "Boil the water.\nAdd the pasta.\nDrain it."}
            ],
        }
    ]
    monkeypatch.setattr(scraped_data, "instructions", lambda: "Boil the water.\nAdd the pasta.\nDrain it.")

    strategy = RecipeScraperPackage(
        "https://example.com",
        get_locale_provider(),
        repos=None,  # type: ignore[arg-type]
    )
    recipe, _ = strategy.clean_scraper(scraped_data, "https://example.com")
    steps = recipe.recipe_instructions
    assert steps is not None

    assert [step.text for step in steps] == ["Boil the water.", "Add the pasta.", "Drain it."]


def test_step_names_are_kept_as_step_summaries():
    """schema.org names a step with `HowToStep.name`, which is Mealie's `summary`."""
    recipe_data = dict(FLAT_RECIPE)
    recipe_data["recipeInstructions"] = [
        {"@type": "HowToStep", "name": "Mix", "text": "Whisk the eggs and the sugar."},
        {"@type": "HowToStep", "text": "Fold in the flour."},
    ]

    steps = scrape(recipe_data).recipe_instructions
    assert steps is not None

    assert [(step.summary, step.text) for step in steps] == [
        ("Mix", "Whisk the eggs and the sugar."),
        ("", "Fold in the flour."),
    ]


def test_prefer_structured_instructions_needs_a_heading():
    """Without a heading the structured data says nothing the flat text could not."""
    structured = [{"text": "Dice the onion."}]
    flat = [{"text": "Dice the onion."}]

    assert prefer_structured_instructions(structured, flat) is False


def test_prefer_structured_instructions_keeps_every_piece_of_flat_text():
    structured = [{"text": "Dice the onion.", "title": "Prep"}, {"text": "Brown the beef."}]

    # the flat text is the same content with the heading flattened into a line of its own
    assert prefer_structured_instructions(structured, [{"text": "Prep"}, {"text": "Dice the onion."}]) is True
    # ...but a scraper that read the page itself can produce text the structured data lacks
    assert prefer_structured_instructions(structured, [{"text": "Dice the onion, finely."}]) is False


def test_prefer_structured_instructions_ignores_a_stringified_step_dict():
    """A site nesting one step where a list belongs makes recipe_scrapers hand back a repr."""
    structured = [{"text": "Dice the onion.", "title": "Prep"}]
    flat = [{"text": "{'@type': 'HowToStep', 'text': 'Dice the onion.'}"}]

    assert prefer_structured_instructions(structured, flat) is True
