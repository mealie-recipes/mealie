import random

from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.group_shopping_list import ShoppingListOut
from mealie.schema.labels.multi_purpose_label import MultiPurposeLabelOut
from mealie.services.seeder.seeder_service import SeederService
from tests.utils import api_routes, jsonify
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


def create_labels(api_client: TestClient, unique_user: TestUser, count: int = 10) -> list[MultiPurposeLabelOut]:
    labels: list[MultiPurposeLabelOut] = []
    for _ in range(count):
        response = api_client.post(api_routes.groups_labels, json={"name": random_string()}, headers=unique_user.token)
        labels.append(MultiPurposeLabelOut.model_validate(response.json()))

    return labels


def test_new_list_creates_list_labels(api_client: TestClient, unique_user: TestUser):
    labels = create_labels(api_client, unique_user)
    response = api_client.post(
        api_routes.households_shopping_lists, json={"name": random_string()}, headers=unique_user.token
    )
    new_list = ShoppingListOut.model_validate(response.json())

    assert len(new_list.label_settings) == len(labels)
    label_settings_label_ids = [setting.label_id for setting in new_list.label_settings]
    for label in labels:
        assert label.id in label_settings_label_ids


def test_new_label_creates_list_labels(api_client: TestClient, unique_user: TestUser):
    # create a list with some labels
    create_labels(api_client, unique_user)
    response = api_client.post(
        api_routes.households_shopping_lists, json={"name": random_string()}, headers=unique_user.token
    )
    new_list = ShoppingListOut.model_validate(response.json())
    existing_label_settings = new_list.label_settings

    # create more labels and make sure they were added to the list's label settings
    new_labels = create_labels(api_client, unique_user)
    response = api_client.get(api_routes.households_shopping_lists_item_id(new_list.id), headers=unique_user.token)
    updated_list = ShoppingListOut.model_validate(response.json())
    updated_label_settings = updated_list.label_settings
    assert len(updated_label_settings) == len(existing_label_settings) + len(new_labels)

    label_settings_ids = [setting.id for setting in updated_list.label_settings]
    for label_setting in existing_label_settings:
        assert label_setting.id in label_settings_ids

    label_settings_label_ids = [setting.label_id for setting in updated_list.label_settings]
    for label in new_labels:
        assert label.id in label_settings_label_ids


def test_new_label_creates_list_labels_in_all_households(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser
):
    # unique_user and h2_user are in the same group, so these labels should be for both of them
    create_labels(api_client, unique_user)

    # create a list with some labels for each user
    response = api_client.post(
        api_routes.households_shopping_lists, json={"name": random_string()}, headers=unique_user.token
    )
    new_list_h1 = ShoppingListOut.model_validate(response.json())
    existing_label_settings_h1 = new_list_h1.label_settings

    response = api_client.post(
        api_routes.households_shopping_lists, json={"name": random_string()}, headers=h2_user.token
    )
    new_list_h2 = ShoppingListOut.model_validate(response.json())
    existing_label_settings_h2 = new_list_h2.label_settings

    # create more labels and make sure they were added to both lists' label settings
    new_labels = create_labels(api_client, unique_user)

    for user, new_list, existing_label_settings in [
        (unique_user, new_list_h1, existing_label_settings_h1),
        (h2_user, new_list_h2, existing_label_settings_h2),
    ]:
        response = api_client.get(api_routes.households_shopping_lists_item_id(new_list.id), headers=user.token)
        updated_list = ShoppingListOut.model_validate(response.json())
        updated_label_settings = updated_list.label_settings
        assert len(updated_label_settings) == len(existing_label_settings) + len(new_labels)

        label_settings_ids = [setting.id for setting in updated_list.label_settings]
        for label_setting in existing_label_settings:
            assert label_setting.id in label_settings_ids

        label_settings_label_ids = [setting.label_id for setting in updated_list.label_settings]
        for label in new_labels:
            assert label.id in label_settings_label_ids


def test_seed_label_creates_list_labels(api_client: TestClient, unique_user: TestUser):
    CREATED_LABELS = 32
    database = unique_user.repos

    # create a list with some labels
    create_labels(api_client, unique_user)
    response = api_client.post(
        api_routes.households_shopping_lists, json={"name": random_string()}, headers=unique_user.token
    )
    new_list = ShoppingListOut.model_validate(response.json())
    existing_label_settings = new_list.label_settings

    # seed labels and make sure they were added to the list's label settings
    group = database.groups.get_one(unique_user.group_id)
    assert group
    database = AllRepositories(database.session, group_id=group.id)
    seeder = SeederService(database)
    seeder.seed_labels("en-US")

    response = api_client.get(api_routes.households_shopping_lists_item_id(new_list.id), headers=unique_user.token)
    updated_list = ShoppingListOut.model_validate(response.json())
    updated_label_settings = updated_list.label_settings
    assert len(updated_label_settings) == len(existing_label_settings) + CREATED_LABELS

    label_settings_ids = [setting.id for setting in updated_list.label_settings]
    for label_setting in existing_label_settings:
        assert label_setting.id in label_settings_ids


def test_delete_label_deletes_list_labels(api_client: TestClient, unique_user: TestUser):
    new_labels = create_labels(api_client, unique_user)
    response = api_client.post(
        api_routes.households_shopping_lists, json={"name": random_string()}, headers=unique_user.token
    )
    new_list = ShoppingListOut.model_validate(response.json())

    existing_label_settings = new_list.label_settings
    label_to_delete = random.choice(new_labels)
    api_client.delete(api_routes.groups_labels_item_id(label_to_delete.id), headers=unique_user.token)

    response = api_client.get(api_routes.households_shopping_lists_item_id(new_list.id), headers=unique_user.token)
    updated_list = ShoppingListOut.model_validate(response.json())
    assert len(updated_list.label_settings) == len(existing_label_settings) - 1

    label_settings_label_ids = [setting.label_id for setting in updated_list.label_settings]
    for label in new_labels:
        if label.id == label_to_delete.id:
            assert label.id not in label_settings_label_ids

        else:
            assert label.id in label_settings_label_ids


def test_update_list_doesnt_change_list_labels(api_client: TestClient, unique_user: TestUser):
    create_labels(api_client, unique_user)
    original_name = random_string()
    updated_name = random_string()

    response = api_client.post(
        api_routes.households_shopping_lists, json={"name": original_name}, headers=unique_user.token
    )
    new_list = ShoppingListOut.model_validate(response.json())
    assert new_list.name == original_name
    assert new_list.label_settings

    updated_list_data = new_list.model_dump()
    updated_list_data.pop("created_at", None)
    updated_list_data.pop("updated_at", None)

    updated_list_data["name"] = updated_name
    updated_list_data["label_settings"][0]["position"] = random_int(999, 9999)

    response = api_client.put(
        api_routes.households_shopping_lists_item_id(new_list.id),
        json=jsonify(updated_list_data),
        headers=unique_user.token,
    )
    updated_list = ShoppingListOut.model_validate(response.json())
    assert updated_list.name == updated_name
    assert updated_list.label_settings == new_list.label_settings


def test_update_list_labels(api_client: TestClient, unique_user: TestUser):
    create_labels(api_client, unique_user)
    response = api_client.post(
        api_routes.households_shopping_lists, json={"name": random_string()}, headers=unique_user.token
    )
    new_list = ShoppingListOut.model_validate(response.json())
    changed_setting = random.choice(new_list.label_settings)
    changed_setting.position = random_int(999, 9999)

    response = api_client.put(
        api_routes.households_shopping_lists_item_id_label_settings(new_list.id),
        json=jsonify(new_list.label_settings),
        headers=unique_user.token,
    )
    updated_list = ShoppingListOut.model_validate(response.json())

    original_settings_by_id = {setting.id: setting for setting in new_list.label_settings}
    for setting in updated_list.label_settings:
        assert setting.id in original_settings_by_id
        assert original_settings_by_id[setting.id].shopping_list_id == setting.shopping_list_id
        assert original_settings_by_id[setting.id].label_id == setting.label_id

        if setting.id == changed_setting.id:
            assert setting.position == changed_setting.position

        else:
            assert original_settings_by_id[setting.id].position == setting.position


def test_list_label_order(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(
        api_routes.households_shopping_lists, json={"name": random_string()}, headers=unique_user.token
    )
    new_list = ShoppingListOut.model_validate(response.json())
    for i, setting in enumerate(new_list.label_settings):
        if not i:
            continue

        assert setting.position > new_list.label_settings[i - 1].position

    random.shuffle(new_list.label_settings)
    response = api_client.put(
        api_routes.households_shopping_lists_item_id_label_settings(new_list.id),
        json=jsonify(new_list.label_settings),
        headers=unique_user.token,
    )
    updated_list = ShoppingListOut.model_validate(response.json())
    for i, setting in enumerate(updated_list.label_settings):
        if not i:
            continue

        assert setting.position > updated_list.label_settings[i - 1].position
