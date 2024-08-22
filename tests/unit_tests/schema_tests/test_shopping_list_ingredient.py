import uuid

from mealie.schema.household.group_shopping_list import ShoppingListItemOut


def test_shopping_list_ingredient_validation():
    db_obj = {
        "quantity": 8,
        "unit": None,
        "food": {
            "id": "4cf32eeb-d136-472d-86c7-287b6328d21f",
            "name": "bell peppers",
            "pluralName": None,
            "description": "",
            "extras": {},
            "labelId": None,
            "aliases": [],
            "label": None,
            "createdAt": "2024-02-26T18:29:46.190754",
            "updatedAt": "2024-02-26T18:29:46.190758",
        },
        "note": "",
        "isFood": True,
        "disableAmount": False,
        "shoppingListId": "dc8bce82-2da9-49f0-94e6-6d69d311490e",
        "checked": False,
        "position": 5,
        "foodId": "4cf32eeb-d136-472d-86c7-287b6328d21f",
        "labelId": None,
        "unitId": None,
        "extras": {},
        "id": "80f4df25-6139-4d30-be0c-4100f50e5396",
        "label": None,
        "recipeReferences": [],
        "groupId": uuid.uuid4(),
        "householdId": uuid.uuid4(),
        "createdAt": "2024-02-27T10:18:19.274677",
        "updatedAt": "2024-02-27T11:26:32.643392",
    }
    out = ShoppingListItemOut.model_validate(db_obj)
    assert out.display == "8 bell peppers"
