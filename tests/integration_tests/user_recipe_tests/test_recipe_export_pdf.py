from fastapi.testclient import TestClient

from mealie.schema.cookbook.cookbook import CookBookSave
from mealie.schema.recipe.recipe import RecipeDraft, RecipeOut
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_notes import RecipeNote
from mealie.schema.recipe.recipe_step import RecipeStep
from tests import data
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def _pdf_titles_match(content: bytes, name: str) -> bool:
    # fpdf2 writes outline (bookmark) titles as uncompressed PDF strings, so recipe names show up
    # verbatim in the file when they are ASCII.
    return f"({name})".encode() in content


def _create_recipe(user: TestUser, name: str, extra_ingredients: int = 0) -> RecipeOut:
    extras = [RecipeIngredient(note=f"{i} tbsp sugar") for i in range(extra_ingredients)]
    return user.repos.recipes.create(
        RecipeDraft(
            user_id=user.user_id,
            group_id=user.group_id,
            household_id=user.household_id,
            name=name,
            description="Crème brûlée, ½ cup – Ελληνικά, Кириллица",
            recipe_ingredient=[
                RecipeIngredient(title="Base", note="2 cups cream"),
                RecipeIngredient(note="5 yolks"),
                *extras,
            ],
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

    cookbook = _create_cookbook(unique_user, prefix)

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


def _create_cookbook(user: TestUser, name_prefix: str) -> CookBookSave:
    return user.repos.cookbooks.create(
        CookBookSave(
            name=random_string(),
            group_id=user.group_id,
            household_id=user.household_id,
            query_filter_string=f'name LIKE "{name_prefix}%"',
        )
    )


def test_get_large_cookbook_as_pdf(api_client: TestClient, unique_user: TestUser) -> None:
    # 30 recipes overflow the first contents page (28 rows), 8 ingredient rows switch to two columns,
    # and an uploaded image exercises the banner path.
    prefix = random_string(8)
    names = sorted(f"{prefix}{i:02d}" for i in range(30))
    recipes = [_create_recipe(unique_user, name, extra_ingredients=6) for name in names]

    response = api_client.put(
        api_routes.recipes_slug_image(recipes[0].slug),
        data={"extension": "jpg"},
        files={"image": data.images_test_image_1.read_bytes()},
        headers=unique_user.token,
    )
    assert response.status_code == 200

    cookbook = _create_cookbook(unique_user, prefix)
    response = api_client.get(api_routes.households_cookbooks_item_id_pdf(cookbook.id), headers=unique_user.token)

    assert response.status_code == 200
    assert response.content.startswith(b"%PDF-")
    assert _pdf_titles_match(response.content, names[0])
    assert _pdf_titles_match(response.content, names[-1])
    assert b"/Subtype /Image" in response.content


def test_get_empty_cookbook_as_pdf(api_client: TestClient, unique_user: TestUser) -> None:
    cookbook = _create_cookbook(unique_user, random_string(12))

    response = api_client.get(api_routes.households_cookbooks_item_id_pdf(cookbook.id), headers=unique_user.token)

    assert response.status_code == 200
    assert b"/Count 1" in response.content
