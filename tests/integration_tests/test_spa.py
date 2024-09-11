import pytest
from bs4 import BeautifulSoup

from mealie.routes import spa
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_share_token import RecipeShareTokenSave
from tests import data as test_data
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


@pytest.fixture(autouse=True)
def set_spa_contents():
    """Inject a simple HTML string into the SPA module to enable metadata injection"""

    spa.__contents = "<!DOCTYPE html><html><head></head><body></body></html>"


def set_group_is_private(unique_user: TestUser, *, is_private: bool):
    group = unique_user.repos.groups.get_by_slug_or_id(unique_user.group_id)
    assert group and group.preferences
    group.preferences.private_group = is_private
    unique_user.repos.group_preferences.update(group.id, group.preferences)


def set_recipe_is_public(unique_user: TestUser, recipe: Recipe, *, is_public: bool):
    assert recipe.settings
    recipe.settings.public = is_public
    unique_user.repos.recipes.update(recipe.slug, recipe)


def create_recipe(user: TestUser) -> Recipe:
    recipe = user.repos.recipes.create(
        Recipe(
            user_id=user.user_id,
            group_id=user.group_id,
            name=random_string(),
        )
    )
    set_group_is_private(user, is_private=False)
    set_recipe_is_public(user, recipe, is_public=True)

    return recipe


def test_spa_metadata_injection():
    fp = test_data.html_mealie_recipe
    with open(fp) as f:
        soup = BeautifulSoup(f, "lxml")
        assert soup.html and soup.html.head

        tags = soup.find_all("meta")
        assert tags

        title_tag = None
        for tag in tags:
            if tag.get("data-hid") == "og:title":
                title_tag = tag
                break

        assert title_tag and title_tag["content"]

        new_title_tag = spa.MetaTag(hid="og:title", property_name="og:title", content=random_string())
        new_arbitrary_tag = spa.MetaTag(hid=random_string(), property_name=random_string(), content=random_string())
        new_html = spa.inject_meta(str(soup), [new_title_tag, new_arbitrary_tag])

    # verify changes were injected
    soup = BeautifulSoup(new_html, "lxml")
    assert soup.html and soup.html.head

    tags = soup.find_all("meta")
    assert tags

    title_tag = None
    for tag in tags:
        if tag.get("data-hid") == "og:title":
            title_tag = tag
            break

    assert title_tag and title_tag["content"] == new_title_tag.content

    arbitrary_tag = None
    for tag in tags:
        if tag.get("data-hid") == new_arbitrary_tag.hid:
            arbitrary_tag = tag
            break

    assert arbitrary_tag and arbitrary_tag["content"] == new_arbitrary_tag.content


def test_spa_recipe_json_injection():
    recipe_name = random_string()
    schema = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": recipe_name,
    }

    fp = test_data.html_mealie_recipe
    with open(fp) as f:
        soup = BeautifulSoup(f, "lxml")
        assert "https://schema.org" not in str(soup)

        html = spa.inject_recipe_json(str(soup), schema)

    assert "@context" in html
    assert "https://schema.org" in html
    assert recipe_name in html


@pytest.mark.parametrize("use_public_user", [True, False])
@pytest.mark.asyncio
async def test_spa_serve_recipe_with_meta(unique_user: TestUser, use_public_user: bool):
    recipe = create_recipe(unique_user)
    user = unique_user.repos.users.get_by_username(unique_user.username)
    assert user

    response = await spa.serve_recipe_with_meta(
        user.group_slug, recipe.slug, user=None if use_public_user else user, session=unique_user.repos.session
    )
    assert response.status_code == 200
    assert "https://schema.org" in response.body.decode()


@pytest.mark.parametrize("use_public_user", [True, False])
@pytest.mark.asyncio
async def test_spa_serve_recipe_with_meta_invalid_data(unique_user: TestUser, use_public_user: bool):
    recipe = create_recipe(unique_user)
    user = unique_user.repos.users.get_by_username(unique_user.username)
    assert user

    response = await spa.serve_recipe_with_meta(
        random_string(), recipe.slug, user=None if use_public_user else user, session=unique_user.repos.session
    )
    assert response.status_code == 404

    response = await spa.serve_recipe_with_meta(
        user.group_slug, random_string(), user=None if use_public_user else user, session=unique_user.repos.session
    )
    assert response.status_code == 404

    set_recipe_is_public(unique_user, recipe, is_public=False)
    response = await spa.serve_recipe_with_meta(
        user.group_slug, recipe.slug, user=None if use_public_user else user, session=unique_user.repos.session
    )
    if use_public_user:
        assert response.status_code == 404
    else:
        assert response.status_code == 200

    set_group_is_private(unique_user, is_private=True)
    set_recipe_is_public(unique_user, recipe, is_public=True)
    response = await spa.serve_recipe_with_meta(
        user.group_slug, recipe.slug, user=None if use_public_user else user, session=unique_user.repos.session
    )
    if use_public_user:
        assert response.status_code == 404
    else:
        assert response.status_code == 200


@pytest.mark.parametrize("use_private_group", [True, False])
@pytest.mark.parametrize("use_public_recipe", [True, False])
@pytest.mark.asyncio
async def test_spa_service_shared_recipe_with_meta(
    unique_user: TestUser, use_private_group: bool, use_public_recipe: bool
):
    group = unique_user.repos.groups.get_by_slug_or_id(unique_user.group_id)
    assert group
    recipe = create_recipe(unique_user)

    # visibility settings shouldn't matter for shared recipes
    set_group_is_private(unique_user, is_private=use_private_group)
    set_recipe_is_public(unique_user, recipe, is_public=use_public_recipe)

    token = unique_user.repos.recipe_share_tokens.create(
        RecipeShareTokenSave(recipe_id=recipe.id, group_id=unique_user.group_id)
    )

    response = await spa.serve_shared_recipe_with_meta(group.slug, token.id, session=unique_user.repos.session)
    assert response.status_code == 200
    assert "https://schema.org" in response.body.decode()


@pytest.mark.asyncio
async def test_spa_service_shared_recipe_with_meta_invalid_data(unique_user: TestUser):
    group = unique_user.repos.groups.get_by_slug_or_id(unique_user.group_id)
    assert group

    response = await spa.serve_shared_recipe_with_meta(group.slug, random_string(), session=unique_user.repos.session)
    assert response.status_code == 404
