from fastapi.testclient import TestClient

from mealie.schema.cookbook.cookbook import CookBookSave
from mealie.schema.recipe.recipe import RecipeDraft, RecipeOut
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_notes import RecipeNote
from mealie.schema.recipe.recipe_step import RecipeStep
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def _pdf_titles_match(content: bytes, name: str) -> bool:
    # fpdf2 writes outline (bookmark) titles as uncompressed PDF strings, so recipe names show up
    # verbatim in the file when they are ASCII.
    return f"({name})".encode() in content


def _create_recipe(user: TestUser, name: str) -> RecipeOut:
    return user.repos.recipes.create(
        RecipeDraft(
            user_id=user.user_id,
            group_id=user.group_id,
            household_id=user.household_id,
            name=name,
            description="Crème brûlée, ½ cup – Ελληνικά, Кириллица",
            recipe_ingredient=[RecipeIngredient(title="Base", note="2 cups cream"), RecipeIngredient(note="5 yolks")],
            recipe_instructions=[RecipeStep(title="Cook", summary="Heat", text="Heat the cream. " * 40)],
            notes=[RecipeNote(title="Tip", text="Make ahead.")],
        )
    )


def test_get_recipe_as_pdf(api_client: TestClient, unique_user: TestUser) -> None:
    recipe = _create_recipe(unique_user, random_string())

    response = api_client.get(api_routes.recipes_slug_exports_pdf(recipe.slug), headers=unique_user.token)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert f'filename="{recipe.slug}.pdf"' in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF-")


def test_get_recipe_as_pdf_other_group_not_found(
    api_client: TestClient, unique_user: TestUser, g2_user: TestUser
) -> None:
    recipe = _create_recipe(g2_user, random_string())

    response = api_client.get(api_routes.recipes_slug_exports_pdf(recipe.slug), headers=unique_user.token)

    assert response.status_code == 404


def test_get_cookbook_as_pdf_only_includes_group_recipes(
    api_client: TestClient, unique_user: TestUser, g2_user: TestUser
) -> None:
    prefix = random_string(8)
    in_book = [f"{prefix}{random_string(6)}" for _ in range(3)]
    for name in in_book:
        _create_recipe(unique_user, name)
    not_in_book = _create_recipe(unique_user, random_string()).name
    other_group = _create_recipe(g2_user, f"{prefix}{random_string(6)}").name

    cookbook = unique_user.repos.cookbooks.create(
        CookBookSave(
            name=random_string(),
            group_id=unique_user.group_id,
            household_id=unique_user.household_id,
            query_filter_string=f'name LIKE "{prefix}%"',
        )
    )

    response = api_client.get(api_routes.households_cookbooks_item_id_pdf(cookbook.id), headers=unique_user.token)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    for name in in_book:
        assert _pdf_titles_match(response.content, name)
    assert not _pdf_titles_match(response.content, not_in_book)
    assert not _pdf_titles_match(response.content, other_group)


def test_get_cookbook_as_pdf_other_group_not_found(
    api_client: TestClient, unique_user: TestUser, g2_user: TestUser
) -> None:
    cookbook = g2_user.repos.cookbooks.create(
        CookBookSave(name=random_string(), group_id=g2_user.group_id, household_id=g2_user.household_id)
    )

    response = api_client.get(api_routes.households_cookbooks_item_id_pdf(cookbook.id), headers=unique_user.token)

    assert response.status_code == 404
