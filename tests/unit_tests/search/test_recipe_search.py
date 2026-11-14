from uuid import UUID

import pytest
import sqlalchemy as sa

from mealie.schema.recipe import IngredientFoodSave, RecipeDraft, RecipeIngredient
from mealie.schema.response.pagination import PaginationQuery
from mealie.search.index import rebuild
from tests.utils.fixture_schemas import TestUser


@pytest.fixture()
def unique_user(unique_user_fn_scoped: TestUser) -> TestUser:
    return unique_user_fn_scoped


@pytest.fixture()
def recipes(unique_user: TestUser) -> dict[str, str]:
    names = {
        "target": "Sesame-Lime Lettuce Cups with Pork, Red Chili Peppers & Cilantro",
        "pork": "Pork Chops",
        "chicken": "Chicken Lettuce Cups",
        "wrap": "Beef Tortilla Wrap",
        "boundary": "Porker Bowl",
    }
    result = {}
    for key, name in names.items():
        recipe = unique_user.repos.recipes.create(
            RecipeDraft(
                name=name,
                user_id=unique_user.user_id,
                group_id=unique_user.group_id,
                recipe_ingredient=[RecipeIngredient(note="ground pork"), RecipeIngredient(note="butter lettuce")]
                if key == "target"
                else [],
            )
        )
        result[key] = str(recipe.id)
    return result


def search(user: TestUser, query: str, **kwargs):
    return user.repos.recipes.page_all(PaginationQuery(per_page=50, order_by="name"), search=query, **kwargs)


def test_concept_search(unique_user: TestUser, recipes: dict[str, str]) -> None:
    page = search(unique_user, "pork lettuce wrap")
    assert [str(item.id) for item in page.items] == [recipes["target"]]
    assert page.total == 1
    assert search(unique_user, "pork lettuce wrap", search_mode="any").total == 3
    assert [str(item.id) for item in search(unique_user, 'pork "lettuce cups"').items] == [recipes["target"]]
    assert search(unique_user, "pork lettuce wrap -cilantro").total == 0
    assert search(unique_user, "+pork lettuce wrap", search_mode="any").total == 1
    assert search(unique_user, '+pork -"chili peppers"').total == 1
    assert search(unique_user, "+pork").total == 2
    assert search(unique_user, '-"lettuce cups"').total == 3


def test_phrase_boundaries_and_full_text(unique_user: TestUser) -> None:
    recipe = unique_user.repos.recipes.create(
        RecipeDraft(
            name="界面炒饭 Crème Brûlée ΟΣ ΜΟΥΣΑΚΆΣ Борщ",
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            description="x " * 200 + "distant saffron",
            recipe_ingredient=[RecipeIngredient(note="red chili"), RecipeIngredient(note="peppers")],
        )
    )
    assert search(unique_user, "界面炒饭").total == 1
    assert search(unique_user, '"creme brulee"').total == 1
    assert search(unique_user, "ος").total == 1
    assert search(unique_user, "μουσακάς").total == 1
    assert search(unique_user, "борщ").total == 1
    assert search(unique_user, "saffron").total == 1
    assert search(unique_user, '"chili peppers"').total == 0
    assert search(unique_user, "chili peppers").total == 1
    assert str(search(unique_user, "creme").items[0].id) == str(recipe.id)


def test_sql_bulk_updates_rollback_and_rebuild(unique_user: TestUser, recipes: dict[str, str]) -> None:
    from mealie.db.models.recipe.recipe import RecipeModel

    session = unique_user.repos.session
    target_id = UUID(recipes["target"])
    session.execute(sa.update(RecipeModel).where(RecipeModel.id == target_id).values(name="Cardamom Soufflé"))
    assert search(unique_user, '"cardamom souffle"').total == 1
    session.rollback()
    assert search(unique_user, "pork lettuce wrap").total == 1
    session.execute(
        sa.text("DELETE FROM recipe_search_segments WHERE recipe_id=CAST(:id AS TEXT)"),
        {"id": target_id.hex if session.get_bind().dialect.name == "sqlite" else str(target_id)},
    )
    assert search(unique_user, "pork lettuce wrap").total == 0
    rebuild(session.connection())
    assert search(unique_user, "pork lettuce wrap").total == 1
    unique_user.repos.recipes.delete(target_id, match_key="id")
    assert search(unique_user, "pork lettuce wrap").total == 0


def test_structured_food_rename(unique_user: TestUser) -> None:
    food = unique_user.repos.ingredient_foods.create(IngredientFoodSave(name="Saffron", group_id=unique_user.group_id))
    unique_user.repos.recipes.create(
        RecipeDraft(
            name="Golden Rice",
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            recipe_ingredient=[RecipeIngredient(food=food)],
        )
    )
    assert search(unique_user, "saffron").total == 1
    from mealie.db.models.recipe.ingredient import IngredientFoodModel

    unique_user.repos.session.execute(
        sa.update(IngredientFoodModel).where(IngredientFoodModel.id == food.id).values(name="Turmeric")
    )
    assert search(unique_user, "saffron").total == 0
    assert search(unique_user, "turmeric").total == 1
    unique_user.repos.session.rollback()
    assert search(unique_user, "saffron").total == 1


def test_other_group_does_not_supply_results_or_corrections(unique_user: TestUser, g2_user: TestUser) -> None:
    g2_user.repos.recipes.create(RecipeDraft(name="Mushroom Stew", user_id=g2_user.user_id, group_id=g2_user.group_id))
    assert search(unique_user, "mushroom").total == 0
    assert search(unique_user, "mushrom").total == 0


def test_endpoint_validation(api_client, unique_user: TestUser, recipes: dict[str, str]) -> None:
    response = api_client.get("/api/recipes", params={"search": '"unfinished'}, headers=unique_user.token)
    assert response.status_code == 422
    response = api_client.get(
        "/api/recipes", params={"search": "+pork lettuce wrap", "searchMode": "any"}, headers=unique_user.token
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_filter_scopes_typo_vocabulary(unique_user: TestUser) -> None:
    inside = unique_user.repos.recipes.create(
        RecipeDraft(name="Mushroom Stew", user_id=unique_user.user_id, group_id=unique_user.group_id)
    )
    unique_user.repos.recipes.create(
        RecipeDraft(name="Mushrom Soup", user_id=unique_user.user_id, group_id=unique_user.group_id)
    )
    page = unique_user.repos.recipes.page_all(PaginationQuery(query_filter=f"id = {inside.id}"), search="mushrom")
    assert [item.id for item in page.items] == [inside.id]


def test_index_downgrade_and_reinstall(unique_user: TestUser, recipes: dict[str, str]) -> None:
    from mealie.search.index import install, uninstall

    connection = unique_user.repos.session.connection()
    uninstall(connection)
    install(connection)
    unique_user.repos.session.commit()
    assert [str(item.id) for item in search(unique_user, "pork lettuce wrap").items] == [recipes["target"]]


def test_search_window_counts_and_empty_pages(unique_user: TestUser, recipes: dict[str, str]) -> None:
    repo = unique_user.repos.recipes
    for number in (1, 2, 4):
        page = repo.page_all(PaginationQuery(page=number, per_page=1), search="pork lettuce wrap", search_mode="any")
        assert page.total == 3
        assert page.total_pages == 3
        assert len(page.items) == (0 if number == 4 else 1)
    assert repo.page_all(PaginationQuery(per_page=-1), search="+pork").total == 2
    last = repo.page_all(PaginationQuery(page=-1, per_page=1), search="+pork")
    assert last.total == 2 and last.page == 2


def test_autogenerate_preserves_derived_search_tables(unique_user: TestUser) -> None:
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext
    from sqlalchemy import MetaData

    from mealie.search.index import include_name

    connection = unique_user.repos.session.connection()
    context = MigrationContext.configure(connection, opts={"include_name": include_name})
    differences = compare_metadata(context, MetaData())
    dropped_names = {item[1].name for item in differences if item[0] == "remove_table"}
    assert not any(name.startswith("recipe_search_") for name in dropped_names)


@pytest.mark.parametrize(
    ("singular", "plural"),
    [
        ("tomato", "tomatoes"),
        ("potato", "potatoes"),
        ("cookie", "cookies"),
        ("chili", "chilies"),
        ("berry", "berries"),
        ("taco", "tacos"),
        ("pea", "peas"),
        ("egg", "eggs"),
        ("dish", "dishes"),
    ],
)
def test_common_plurals_in_multiple_concepts(unique_user: TestUser, singular: str, plural: str) -> None:
    for name in (f"{plural} Pasta", f"{singular} Pasta"):
        unique_user.repos.recipes.create(
            RecipeDraft(name=name, user_id=unique_user.user_id, group_id=unique_user.group_id)
        )
    assert search(unique_user, f"{singular} pasta").total == 2
    assert search(unique_user, f"{plural} pasta").total == 2
    assert search(unique_user, f"+{singular} pasta").total == 1
