import pytest

from mealie.schema.cookbook.cookbook import CookBookSave
from mealie.schema.recipe import RecipeDraft
from mealie.schema.response.pagination import PaginationQuery
from tests.utils.fixture_schemas import TestUser


@pytest.mark.parametrize("use_cookbook", [False, True], ids=["query_filter", "cookbook"])
@pytest.mark.parametrize("outside_name", ["Safron Rice", "Saffron Rice"], ids=["exact_match", "ambiguous_correction"])
def test_filter_scopes_typo_vocabulary(unique_user_fn_scoped: TestUser, use_cookbook: bool, outside_name: str) -> None:
    user = unique_user_fn_scoped
    target = user.repos.recipes.create(RecipeDraft(name="Safran Rice", user_id=user.user_id, group_id=user.group_id))
    user.repos.recipes.create(RecipeDraft(name=outside_name, user_id=user.user_id, group_id=user.group_id))
    query_filter = f"id IN [{target.id}]"
    pagination = PaginationQuery(per_page=50, order_by="name", query_filter=None if use_cookbook else query_filter)
    cookbook = (
        user.repos.cookbooks.create(
            CookBookSave(
                name="Scoped Search",
                group_id=user.group_id,
                household_id=user.household_id,
                query_filter_string=query_filter,
            )
        )
        if use_cookbook
        else None
    )

    page = user.repos.recipes.page_all(pagination, cookbook=cookbook, search="safron")

    assert [recipe.id for recipe in page.items] == [target.id]
    assert page.total == 1
