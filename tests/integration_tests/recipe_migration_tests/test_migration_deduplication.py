from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from threading import Barrier
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient

from tests.integration_tests.recipe_migration_tests.test_duplicate_migration_images import archive_for
from tests.utils.fixture_schemas import TestUser


def migrate(
    client: TestClient, user: TestUser, kind: str = "copymethat", *, copy: bool = False, archive: bytes | None = None
) -> dict:
    data = {"migration_type": kind}
    if copy:
        data["skip_duplicates"] = "false"
    response = client.post(
        "/api/groups/migrations",
        data=data,
        files={"archive": ("recipes.zip", archive or archive_for(kind, True), "application/zip")},
        headers=user.token,
    )
    assert response.status_code == 200, response.text
    report = client.get(f"/api/groups/reports/{response.json()['id']}", headers=user.token).json()
    assert report["status"] == "success", report
    return report


def recipes(client: TestClient, user: TestUser) -> list[dict]:
    return client.get(
        "/api/recipes", headers=user.token, params={"queryFilter": f"household_id={user.household_id}"}
    ).json()["items"]


@pytest.mark.parametrize("kind", ["copymethat", "tandoor", "nextcloud"])
def test_default_skip_preserves_user_edits(api_client: TestClient, unique_user_fn_scoped: TestUser, kind: str) -> None:
    user = unique_user_fn_scoped
    migrate(api_client, user, kind)
    original = recipes(api_client, user)[0]
    recipe = user.repos.recipes.get_one(original["id"], "id")
    recipe.description = "User's changes must survive reimport"
    user.repos.recipes.update(recipe.slug, recipe)
    report = migrate(api_client, user, kind, archive=archive_for(kind, False))
    assert "Skipped duplicate" in report["entries"][0]["message"]
    remaining = recipes(api_client, user)
    assert len(remaining) == 1
    assert remaining[0]["id"] == original["id"]
    detail = api_client.get(f"/api/recipes/{remaining[0]['slug']}", headers=user.token).json()
    assert detail["description"] == "User's changes must survive reimport"
    assert remaining[0]["image"] == original["image"]


def test_copy_mode_then_default_skip(api_client: TestClient, unique_user_fn_scoped: TestUser) -> None:
    user = unique_user_fn_scoped
    migrate(api_client, user, copy=True)
    migrate(api_client, user, copy=True)
    assert len(recipes(api_client, user)) == 2
    report = migrate(api_client, user)
    assert len(recipes(api_client, user)) == 2
    assert "Skipped duplicate" in report["entries"][0]["message"]


def test_same_name_different_contents_are_not_duplicates(
    api_client: TestClient, unique_user_fn_scoped: TestUser
) -> None:
    user = unique_user_fn_scoped
    migrate(api_client, user)
    output = BytesIO()
    with ZipFile(BytesIO(archive_for("copymethat", True))) as source, ZipFile(output, "w") as target:
        for name in source.namelist():
            content = source.read(name)
            target.writestr(name, content.replace(b"1 egg", b"2 eggs") if name.endswith(".html") else content)
    migrate(api_client, user, archive=output.getvalue())
    assert len(recipes(api_client, user)) == 2


def test_import_sources_are_independent(api_client: TestClient, unique_user_fn_scoped: TestUser) -> None:
    user = unique_user_fn_scoped
    migrate(api_client, user, "copymethat")
    migrate(api_client, user, "nextcloud")
    assert len(recipes(api_client, user)) == 2


def test_deleted_recipe_can_be_imported_again(api_client: TestClient, unique_user_fn_scoped: TestUser) -> None:
    user = unique_user_fn_scoped
    migrate(api_client, user)
    first = recipes(api_client, user)[0]
    response = api_client.delete(f"/api/recipes/{first['slug']}", headers=user.token)
    assert response.status_code == 200
    migrate(api_client, user)
    remaining = recipes(api_client, user)
    assert len(remaining) == 1
    assert remaining[0]["id"] != first["id"]


def test_concurrent_imports_create_one_recipe(api_client: TestClient, unique_user_fn_scoped: TestUser) -> None:
    barrier = Barrier(2)
    user = unique_user_fn_scoped

    def run() -> dict:
        barrier.wait(timeout=10)
        return migrate(api_client, user)

    with ThreadPoolExecutor(max_workers=2) as executor:
        reports = list(executor.map(lambda _: run(), range(2)))
    assert len(recipes(api_client, user)) == 1
    assert sum("Skipped duplicate" in entry["message"] for report in reports for entry in report["entries"]) == 1


def test_households_do_not_deduplicate_each_other(
    api_client: TestClient, unique_user: TestUser, h2_user: TestUser
) -> None:
    assert unique_user.group_id == h2_user.group_id
    assert unique_user.household_id != h2_user.household_id
    migrate(api_client, unique_user)
    migrate(api_client, h2_user)
    assert len(recipes(api_client, unique_user)) == 1
    assert len(recipes(api_client, h2_user)) == 1
    assert recipes(api_client, unique_user)[0]["id"] != recipes(api_client, h2_user)[0]["id"]


def test_failed_identity_write_rolls_back_recipe(api_client: TestClient, unique_user_fn_scoped: TestUser) -> None:
    from sqlalchemy import event

    from mealie.db.models.recipe.migration import RecipeMigrationModel

    def fail(*args: object) -> None:
        raise RuntimeError("Simulated identity write failure")

    user = unique_user_fn_scoped
    event.listen(RecipeMigrationModel, "before_insert", fail)
    try:
        response = api_client.post(
            "/api/groups/migrations",
            data={"migration_type": "copymethat"},
            files={"archive": ("recipes.zip", archive_for("copymethat", True), "application/zip")},
            headers=user.token,
        )
        assert response.status_code == 200
        report = api_client.get(f"/api/groups/reports/{response.json()['id']}", headers=user.token).json()
        assert report["status"] == "failure"
        assert not recipes(api_client, user)
    finally:
        event.remove(RecipeMigrationModel, "before_insert", fail)
    migrate(api_client, user)
    assert len(recipes(api_client, user)) == 1


def test_repeated_recipes_in_one_archive_are_skipped(api_client: TestClient, unique_user_fn_scoped: TestUser) -> None:
    output = BytesIO()
    with ZipFile(BytesIO(archive_for("copymethat", True))) as source, ZipFile(output, "w") as target:
        for name in source.namelist():
            content = source.read(name)
            target.writestr(name, content * 2 if name.endswith(".html") else content)
    report = migrate(api_client, unique_user_fn_scoped, archive=output.getvalue())
    assert len(recipes(api_client, unique_user_fn_scoped)) == 1
    assert sum("Skipped duplicate" in entry["message"] for entry in report["entries"]) == 1


def test_identity_conflict_rolls_back_new_recipe(
    api_client: TestClient,
    unique_user_fn_scoped: TestUser,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import sqlalchemy as sa

    from mealie.db.models.recipe.migration import RecipeMigrationModel
    from mealie.repos.repository_recipes import DuplicateRecipeImport
    from mealie.schema.recipe import Recipe

    user = unique_user_fn_scoped
    migrate(api_client, user)
    repo = user.repos.recipes
    fingerprint = repo.session.scalar(
        sa.select(RecipeMigrationModel.fingerprint).where(
            RecipeMigrationModel.household_id == user._household_id,
        )
    )
    assert fingerprint is not None
    lookup = repo.get_imported_recipe
    calls = 0

    def stale_lookup(source: str, content_hash: str) -> Recipe | None:
        nonlocal calls
        calls += 1
        # Emulate another transaction committing after our initial lookup.
        return None if calls == 1 else lookup(source, content_hash)

    monkeypatch.setattr(repo, "get_imported_recipe", stale_lookup)
    candidate = Recipe(name="Different slug avoids a slug conflict", user_id=user.user_id, group_id=user._group_id)
    with pytest.raises(DuplicateRecipeImport):
        repo.create_imported(candidate, "copymethat", fingerprint, skip_duplicates=True)
    assert len(recipes(api_client, user)) == 1
