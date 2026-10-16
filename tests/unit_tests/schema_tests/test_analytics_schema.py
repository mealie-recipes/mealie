import uuid
import pytest
from pydantic import ValidationError
from mealie.schema.analytics.analytics import MealieAnalytics


def test_mealie_analytics_valid():
    data = {
        "installation_id": str(uuid.uuid4()),
        "version": "v1.0.0",
        "database_type": "sqlite",
        "using_email": True,
        "using_ldap": False,
        "api_tokens": 5,
        "users": 10,
        "groups": 2,
        "recipes": 100,
        "shopping_lists": 15,
        "cookbooks": 3,
    }

    analytics = MealieAnalytics(**data)

    assert analytics.version == "v1.0.0"
    assert analytics.using_email is True
    assert analytics.recipes == 100


def test_mealie_analytics_invalid_uuid():
    invalid_data = {
        "installation_id": "not-a-valid-uuid",
        "version": "v1.0.0",
        "database_type": "sqlite",
        "using_email": True,
        "using_ldap": False,
        "api_tokens": 1,
        "users": 1,
        "groups": 1,
        "recipes": 1,
        "shopping_lists": 1,
        "cookbooks": 1,
    }

    with pytest.raises(ValidationError):
        MealieAnalytics(**invalid_data)
