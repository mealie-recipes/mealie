"""
Integration tests for:
- GET /organizers/categories/empty, GET /organizers/tags/empty
- POST /organizers/categories/merge, POST /organizers/tags/merge

Categories and tags can also be referenced by two legacy join tables that have no ORM
relationship configured on the Category/Tag models and no FK ondelete cascade:
cookbooks_to_{categories,tags} (cookbook filters) and plan_rules_to_{categories,tags}
(meal plan rules). Deleting a category/tag with rows in either table raises a
ForeignKeyViolation, same failure mode as the food/shopping-list-item bug.

These join tables are populated only by the deprecated `categories`/`tags` relationships on
CookBook/GroupMealPlanRules - the current API (query_filter_string) never writes them - so
existing rows can only come from data created before that migration. To exercise this path,
the tests insert rows into the join tables directly via the ORM session instead of the API.
"""

from fastapi.testclient import TestClient
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from mealie.db.models.recipe.category import cookbooks_to_categories, plan_rules_to_categories
from mealie.db.models.recipe.tag import cookbooks_to_tags, plan_rules_to_tags
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

CATEGORIES_MERGE = "/api/organizers/categories/merge"
TAGS_MERGE = "/api/organizers/tags/merge"


def _create_category(api_client: TestClient, user: TestUser) -> dict:
    response = api_client.post(api_routes.organizers_categories, json={"name": random_string(10)}, headers=user.token)
    assert response.status_code == 201
    return response.json()


def _create_tag(api_client: TestClient, user: TestUser) -> dict:
    response = api_client.post(api_routes.organizers_tags, json={"name": random_string(10)}, headers=user.token)
    assert response.status_code == 201
    return response.json()


def _create_cookbook(api_client: TestClient, user: TestUser) -> dict:
    response = api_client.post(api_routes.households_cookbooks, json={"name": random_string(10)}, headers=user.token)
    assert response.status_code == 201
    return response.json()


def _create_plan_rule(api_client: TestClient, user: TestUser) -> dict:
    response = api_client.post(
        api_routes.households_mealplans_rules,
        json={"day": "unset", "entryType": "unset"},
        headers=user.token,
    )
    assert response.status_code == 201
    return response.json()


def _link_cookbook_to_category(session: Session, cookbook_id: str, category_id: str) -> None:
    session.execute(insert(cookbooks_to_categories).values(cookbook_id=cookbook_id, category_id=category_id))
    session.commit()


def _link_cookbook_to_tag(session: Session, cookbook_id: str, tag_id: str) -> None:
    session.execute(insert(cookbooks_to_tags).values(cookbook_id=cookbook_id, tag_id=tag_id))
    session.commit()


def _link_plan_rule_to_category(session: Session, plan_rule_id: str, category_id: str) -> None:
    session.execute(insert(plan_rules_to_categories).values(group_plan_rule_id=plan_rule_id, category_id=category_id))
    session.commit()


def _link_plan_rule_to_tag(session: Session, plan_rule_id: str, tag_id: str) -> None:
    session.execute(insert(plan_rules_to_tags).values(plan_rule_id=plan_rule_id, tag_id=tag_id))
    session.commit()


# ---------------------------------------------------------------------------
# Categories — empty / direct delete
# ---------------------------------------------------------------------------


def test_category_empty_excludes_category_used_by_cookbook_filter(api_client: TestClient, unique_user: TestUser):
    category = _create_category(api_client, unique_user)
    cookbook = _create_cookbook(api_client, unique_user)
    _link_cookbook_to_category(unique_user.repos.session, cookbook["id"], category["id"])

    response = api_client.get(api_routes.organizers_categories_empty, headers=unique_user.token)
    assert response.status_code == 200
    ids = [c["id"] for c in response.json()]
    assert category["id"] not in ids

    # a direct delete attempt must fail cleanly (not an unhandled 500)
    delete_response = api_client.delete(
        api_routes.organizers_categories_item_id(category["id"]), headers=unique_user.token
    )
    assert delete_response.status_code < 500

    unique_user.repos.session.execute(
        cookbooks_to_categories.delete().where(cookbooks_to_categories.c.cookbook_id == cookbook["id"])
    )
    unique_user.repos.session.commit()
    api_client.delete(api_routes.households_cookbooks_item_id(cookbook["id"]), headers=unique_user.token)
    api_client.delete(api_routes.organizers_categories_item_id(category["id"]), headers=unique_user.token)


def test_category_empty_excludes_category_used_by_plan_rule(api_client: TestClient, unique_user: TestUser):
    category = _create_category(api_client, unique_user)
    plan_rule = _create_plan_rule(api_client, unique_user)
    _link_plan_rule_to_category(unique_user.repos.session, plan_rule["id"], category["id"])

    response = api_client.get(api_routes.organizers_categories_empty, headers=unique_user.token)
    assert response.status_code == 200
    ids = [c["id"] for c in response.json()]
    assert category["id"] not in ids

    delete_response = api_client.delete(
        api_routes.organizers_categories_item_id(category["id"]), headers=unique_user.token
    )
    assert delete_response.status_code < 500

    unique_user.repos.session.execute(
        plan_rules_to_categories.delete().where(plan_rules_to_categories.c.group_plan_rule_id == plan_rule["id"])
    )
    unique_user.repos.session.commit()
    api_client.delete(api_routes.households_mealplans_rules_item_id(plan_rule["id"]), headers=unique_user.token)
    api_client.delete(api_routes.organizers_categories_item_id(category["id"]), headers=unique_user.token)


# ---------------------------------------------------------------------------
# Tags — empty / direct delete
# ---------------------------------------------------------------------------


def test_tag_empty_excludes_tag_used_by_cookbook_filter(api_client: TestClient, unique_user: TestUser):
    tag = _create_tag(api_client, unique_user)
    cookbook = _create_cookbook(api_client, unique_user)
    _link_cookbook_to_tag(unique_user.repos.session, cookbook["id"], tag["id"])

    response = api_client.get(api_routes.organizers_tags_empty, headers=unique_user.token)
    assert response.status_code == 200
    ids = [t["id"] for t in response.json()]
    assert tag["id"] not in ids

    delete_response = api_client.delete(api_routes.organizers_tags_item_id(tag["id"]), headers=unique_user.token)
    assert delete_response.status_code < 500

    unique_user.repos.session.execute(
        cookbooks_to_tags.delete().where(cookbooks_to_tags.c.cookbook_id == cookbook["id"])
    )
    unique_user.repos.session.commit()
    api_client.delete(api_routes.households_cookbooks_item_id(cookbook["id"]), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tags_item_id(tag["id"]), headers=unique_user.token)


def test_tag_empty_excludes_tag_used_by_plan_rule(api_client: TestClient, unique_user: TestUser):
    tag = _create_tag(api_client, unique_user)
    plan_rule = _create_plan_rule(api_client, unique_user)
    _link_plan_rule_to_tag(unique_user.repos.session, plan_rule["id"], tag["id"])

    response = api_client.get(api_routes.organizers_tags_empty, headers=unique_user.token)
    assert response.status_code == 200
    ids = [t["id"] for t in response.json()]
    assert tag["id"] not in ids

    delete_response = api_client.delete(api_routes.organizers_tags_item_id(tag["id"]), headers=unique_user.token)
    assert delete_response.status_code < 500

    unique_user.repos.session.execute(
        plan_rules_to_tags.delete().where(plan_rules_to_tags.c.plan_rule_id == plan_rule["id"])
    )
    unique_user.repos.session.commit()
    api_client.delete(api_routes.households_mealplans_rules_item_id(plan_rule["id"]), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tags_item_id(tag["id"]), headers=unique_user.token)


# ---------------------------------------------------------------------------
# Categories — merge
# ---------------------------------------------------------------------------


def test_category_merge_reassigns_cookbook_filter_and_dedupes_overlap(api_client: TestClient, unique_user: TestUser):
    from_cat = _create_category(api_client, unique_user)
    to_cat = _create_category(api_client, unique_user)
    cookbook = _create_cookbook(api_client, unique_user)

    # one cookbook already references both, to exercise the de-duplication path
    _link_cookbook_to_category(unique_user.repos.session, cookbook["id"], from_cat["id"])
    _link_cookbook_to_category(unique_user.repos.session, cookbook["id"], to_cat["id"])

    response = api_client.post(
        CATEGORIES_MERGE, json={"fromId": from_cat["id"], "toId": to_cat["id"]}, headers=unique_user.token
    )
    assert response.status_code == 200

    rows = unique_user.repos.session.execute(
        select(cookbooks_to_categories.c.category_id).where(cookbooks_to_categories.c.cookbook_id == cookbook["id"])
    ).all()
    category_ids = [str(r[0]) for r in rows]
    assert category_ids.count(to_cat["id"]) == 1
    assert from_cat["id"] not in category_ids

    unique_user.repos.session.execute(
        cookbooks_to_categories.delete().where(cookbooks_to_categories.c.cookbook_id == cookbook["id"])
    )
    unique_user.repos.session.commit()
    api_client.delete(api_routes.households_cookbooks_item_id(cookbook["id"]), headers=unique_user.token)
    api_client.delete(api_routes.organizers_categories_item_id(to_cat["id"]), headers=unique_user.token)


def test_category_merge_reassigns_plan_rule_and_dedupes_overlap(api_client: TestClient, unique_user: TestUser):
    from_cat = _create_category(api_client, unique_user)
    to_cat = _create_category(api_client, unique_user)
    plan_rule = _create_plan_rule(api_client, unique_user)

    _link_plan_rule_to_category(unique_user.repos.session, plan_rule["id"], from_cat["id"])
    _link_plan_rule_to_category(unique_user.repos.session, plan_rule["id"], to_cat["id"])

    response = api_client.post(
        CATEGORIES_MERGE, json={"fromId": from_cat["id"], "toId": to_cat["id"]}, headers=unique_user.token
    )
    assert response.status_code == 200

    rows = unique_user.repos.session.execute(
        select(plan_rules_to_categories.c.category_id).where(
            plan_rules_to_categories.c.group_plan_rule_id == plan_rule["id"]
        )
    ).all()
    category_ids = [str(r[0]) for r in rows]
    assert category_ids.count(to_cat["id"]) == 1
    assert from_cat["id"] not in category_ids

    unique_user.repos.session.execute(
        plan_rules_to_categories.delete().where(plan_rules_to_categories.c.group_plan_rule_id == plan_rule["id"])
    )
    unique_user.repos.session.commit()
    api_client.delete(api_routes.households_mealplans_rules_item_id(plan_rule["id"]), headers=unique_user.token)
    api_client.delete(api_routes.organizers_categories_item_id(to_cat["id"]), headers=unique_user.token)


# ---------------------------------------------------------------------------
# Tags — merge
# ---------------------------------------------------------------------------


def test_tag_merge_reassigns_cookbook_filter_and_dedupes_overlap(api_client: TestClient, unique_user: TestUser):
    from_tag = _create_tag(api_client, unique_user)
    to_tag = _create_tag(api_client, unique_user)
    cookbook = _create_cookbook(api_client, unique_user)

    _link_cookbook_to_tag(unique_user.repos.session, cookbook["id"], from_tag["id"])
    _link_cookbook_to_tag(unique_user.repos.session, cookbook["id"], to_tag["id"])

    response = api_client.post(
        TAGS_MERGE, json={"fromId": from_tag["id"], "toId": to_tag["id"]}, headers=unique_user.token
    )
    assert response.status_code == 200

    rows = unique_user.repos.session.execute(
        select(cookbooks_to_tags.c.tag_id).where(cookbooks_to_tags.c.cookbook_id == cookbook["id"])
    ).all()
    tag_ids = [str(r[0]) for r in rows]
    assert tag_ids.count(to_tag["id"]) == 1
    assert from_tag["id"] not in tag_ids

    unique_user.repos.session.execute(
        cookbooks_to_tags.delete().where(cookbooks_to_tags.c.cookbook_id == cookbook["id"])
    )
    unique_user.repos.session.commit()
    api_client.delete(api_routes.households_cookbooks_item_id(cookbook["id"]), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tags_item_id(to_tag["id"]), headers=unique_user.token)


def test_tag_merge_reassigns_plan_rule_and_dedupes_overlap(api_client: TestClient, unique_user: TestUser):
    from_tag = _create_tag(api_client, unique_user)
    to_tag = _create_tag(api_client, unique_user)
    plan_rule = _create_plan_rule(api_client, unique_user)

    _link_plan_rule_to_tag(unique_user.repos.session, plan_rule["id"], from_tag["id"])
    _link_plan_rule_to_tag(unique_user.repos.session, plan_rule["id"], to_tag["id"])

    response = api_client.post(
        TAGS_MERGE, json={"fromId": from_tag["id"], "toId": to_tag["id"]}, headers=unique_user.token
    )
    assert response.status_code == 200

    rows = unique_user.repos.session.execute(
        select(plan_rules_to_tags.c.tag_id).where(plan_rules_to_tags.c.plan_rule_id == plan_rule["id"])
    ).all()
    tag_ids = [str(r[0]) for r in rows]
    assert tag_ids.count(to_tag["id"]) == 1
    assert from_tag["id"] not in tag_ids

    unique_user.repos.session.execute(
        plan_rules_to_tags.delete().where(plan_rules_to_tags.c.plan_rule_id == plan_rule["id"])
    )
    unique_user.repos.session.commit()
    api_client.delete(api_routes.households_mealplans_rules_item_id(plan_rule["id"]), headers=unique_user.token)
    api_client.delete(api_routes.organizers_tags_item_id(to_tag["id"]), headers=unique_user.token)
