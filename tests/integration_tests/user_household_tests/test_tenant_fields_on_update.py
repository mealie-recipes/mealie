from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from mealie.repos.all_repositories import get_repositories
from mealie.schema.household.group_events import GroupEventNotifierCreate
from mealie.schema.labels.multi_purpose_label import MultiPurposeLabelSave
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_notifier_update_cannot_move_household(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    payload = GroupEventNotifierCreate(name=random_string(), apprise_url=random_string()).model_dump(by_alias=True)
    response = api_client.post(api_routes.households_events_notifications, json=payload, headers=unique_user.token)
    assert response.status_code == 201
    notifier = response.json()

    notifier["householdId"] = str(h2_user.household_id)
    response = api_client.put(
        api_routes.households_events_notifications_item_id(notifier["id"]), json=notifier, headers=unique_user.token
    )
    assert response.status_code == 200

    assert unique_user.repos.group_event_notifier.get_one(notifier["id"])
    assert h2_user.repos.group_event_notifier.get_one(notifier["id"]) is None


def test_label_update_cannot_move_group(api_client: TestClient, unique_user: TestUser, g2_user: TestUser):
    response = api_client.post(api_routes.groups_labels, json={"name": random_string()}, headers=unique_user.token)
    assert response.status_code == 200
    label = response.json()

    label["groupId"] = str(g2_user.group_id)
    response = api_client.put(api_routes.groups_labels_item_id(label["id"]), json=label, headers=unique_user.token)
    assert response.status_code == 200

    assert unique_user.repos.group_multi_purpose_labels.get_one(label["id"])
    assert g2_user.repos.group_multi_purpose_labels.get_one(label["id"]) is None


def test_update_many_cannot_move_group(unique_user: TestUser, g2_user: TestUser):
    label = unique_user.repos.group_multi_purpose_labels.create(
        MultiPurposeLabelSave(name=random_string(), group_id=unique_user.group_id)
    )

    unique_user.repos.group_multi_purpose_labels.update_many([{**label.model_dump(), "group_id": g2_user.group_id}])

    assert unique_user.repos.group_multi_purpose_labels.get_one(label.id)
    assert g2_user.repos.group_multi_purpose_labels.get_one(label.id) is None


def test_unscoped_repo_can_move_group(session: Session, unique_user: TestUser, g2_user: TestUser):
    label = unique_user.repos.group_multi_purpose_labels.create(
        MultiPurposeLabelSave(name=random_string(), group_id=unique_user.group_id)
    )

    unscoped = get_repositories(session, group_id=None, household_id=None)
    moved = unscoped.group_multi_purpose_labels.update(label.id, {**label.model_dump(), "group_id": g2_user.group_id})

    assert str(moved.group_id) == str(g2_user.group_id)


def test_mealplan_update_keeps_owner(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    payload = {"date": datetime.now(UTC).date().strftime("%Y-%m-%d"), "entryType": "dinner", "title": random_string()}
    response = api_client.post(api_routes.households_mealplans, json=payload, headers=unique_user.token)
    assert response.status_code == 201
    plan = response.json()

    plan["userId"] = str(h2_user.user_id)
    response = api_client.put(api_routes.households_mealplans_item_id(plan["id"]), json=plan, headers=unique_user.token)
    assert response.status_code == 200
    assert response.json()["userId"] == str(unique_user.user_id)

    response = api_client.get(api_routes.households_mealplans_item_id(plan["id"]), headers=h2_user.token)
    assert response.status_code == 404


def test_shopping_list_owner_must_be_in_household(
    api_client: TestClient, unique_user: TestUser, unprivileged_user: TestUser, h2_user: TestUser
):
    response = api_client.post(
        api_routes.households_shopping_lists, json={"name": random_string()}, headers=unique_user.token
    )
    assert response.status_code == 201
    shopping_list = response.json()
    route = api_routes.households_shopping_lists_item_id(shopping_list["id"])

    shopping_list["userId"] = str(h2_user.user_id)
    response = api_client.put(route, json=shopping_list, headers=unique_user.token)
    assert response.status_code == 400
    assert h2_user.repos.group_shopping_lists.get_one(shopping_list["id"]) is None

    shopping_list["userId"] = str(uuid4())
    response = api_client.put(route, json=shopping_list, headers=unique_user.token)
    assert response.status_code == 400

    shopping_list["userId"] = str(unprivileged_user.user_id)
    response = api_client.put(route, json=shopping_list, headers=unique_user.token)
    assert response.status_code == 200
    assert response.json()["userId"] == str(unprivileged_user.user_id)
