from mealie.services.recipe.template_service import TemplateService, TemplateType


def test_recipe_export_types() -> None:
    ts = TemplateService()
    assert ts.template_type("recipes.md") == TemplateType.jinja2.value
    assert ts.template_type("raw") == TemplateType.json.value
    assert ts.template_type("zip") == TemplateType.zip.value
