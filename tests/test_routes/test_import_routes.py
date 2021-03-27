import json

import pytest


@pytest.fixture
def backup_data():
    return {
        "name": "dev_sample_data_2021-Feb-13.zip",
        "force": False,
        "recipes": True,
        "settings": False,  #! Broken
        "themes": True,
        "groups": True,
        "users": True,
    }


def test_import(api_client, backup_data):
    response = api_client.post("/api/backups/dev_sample_data_2021-Feb-13.zip/import", json=backup_data)

    assert response.status_code == 200
    for key, value in json.loads(response.content).items():
        for v in value:
            assert v["status"] == True
