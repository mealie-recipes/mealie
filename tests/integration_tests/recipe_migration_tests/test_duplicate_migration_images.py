import json
from io import BytesIO
from zipfile import ZipFile

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from tests.utils.fixture_schemas import TestUser


def archive_for(kind: str, extension: bool, image_format: str = "JPEG", color: str = "red") -> bytes:
    image = BytesIO()
    Image.new("RGB", (40, 40), color).save(image, format=image_format)
    filename = ("full" if kind == "nextcloud" else "image") + ("." + image_format.lower() if extension else "")
    recipe = {
        "name": "Issue 3858 Cake",
        "description": "Reproduction",
        "recipeIngredient": ["1 egg"],
        "recipeInstructions": ["Cook it."],
    }
    output = BytesIO()
    with ZipFile(output, "w") as outer:
        if kind == "tandoor":
            inner = BytesIO()
            with ZipFile(inner, "w") as z:
                z.writestr(
                    "recipe.json",
                    json.dumps(
                        {
                            "name": recipe["name"],
                            "steps": [{"instruction": "Cook it.", "ingredients": []}],
                            "keywords": [],
                            "servings": 1,
                        }
                    ),
                )
                z.writestr(filename, image.getvalue())
            outer.writestr("cake.zip", inner.getvalue())
        elif kind == "nextcloud":
            outer.writestr("cake/recipe.json", json.dumps(recipe))
            outer.writestr("cake/" + filename, image.getvalue())
        else:
            outer.writestr(
                "recipes.html",
                f'<div class="recipe"><h2 id="name">{recipe["name"]}</h2>'
                f'<img class="recipeImage" src="{filename}">'
                '<ul id="recipeIngredients"><li>1 egg</li></ul>'
                '<ol id="recipeInstructions"><li>Cook it.</li></ol></div>',
            )
            outer.writestr(filename, image.getvalue())
    data = output.getvalue()
    return data


@pytest.mark.parametrize("kind", ["copymethat", "tandoor", "nextcloud"])
@pytest.mark.parametrize("sequence", [(True, True), (False, False), (False, True)])
@pytest.mark.parametrize("image_format", ["JPEG", "PNG", "WEBP"])
def test_repeated_migration_images(
    api_client: TestClient,
    unique_user_fn_scoped: TestUser,
    kind: str,
    sequence: tuple[bool, bool],
    image_format: str,
) -> None:
    headers = unique_user_fn_scoped.token
    for count, extension in enumerate(sequence, start=1):
        response = api_client.post(
            "/api/groups/migrations",
            data={"migration_type": kind, "skip_duplicates": "false"},
            files={"archive": ("test.zip", archive_for(kind, extension, image_format), "application/zip")},
            headers=headers,
        )
        assert response.status_code == 200
        recipes = api_client.get("/api/recipes", headers=headers).json()["items"]
        assert len(recipes) == count
        for recipe in recipes:
            assert recipe["image"]
            media = api_client.get(f"/api/media/recipes/{recipe['id']}/images/original.webp")
            assert media.status_code == 200
            with Image.open(BytesIO(media.content)) as image:
                assert image.size == (40, 40)
                red, green, blue = image.convert("RGB").getpixel((20, 20))
                assert red > 200 and green < 30 and blue < 30


@pytest.mark.parametrize("kind", ["copymethat", "tandoor", "nextcloud"])
def test_same_name_recipes_keep_their_own_images(
    api_client: TestClient,
    unique_user_fn_scoped: TestUser,
    kind: str,
) -> None:
    output = BytesIO()
    with ZipFile(output, "w") as merged:
        for index, color in enumerate(["red", "blue"]):
            with ZipFile(BytesIO(archive_for(kind, True, color=color))) as source:
                for name in source.namelist():
                    content = source.read(name)
                    if kind == "tandoor":
                        name = f"cake-{index}.zip"
                    elif kind == "nextcloud":
                        name = name.replace("cake/", f"cake-{index}/")
                    elif name.endswith(".html"):
                        name = f"recipes-{index}.html"
                        content = content.replace(b"image.jpeg", f"image-{index}.jpeg".encode())
                    else:
                        name = f"image-{index}.jpeg"
                    merged.writestr(name, content)
    headers = unique_user_fn_scoped.token
    response = api_client.post(
        "/api/groups/migrations",
        data={"migration_type": kind, "skip_duplicates": "false"},
        files={"archive": ("test.zip", output.getvalue(), "application/zip")},
        headers=headers,
    )
    assert response.status_code == 200
    recipes = api_client.get("/api/recipes", headers=headers).json()["items"]
    assert len(recipes) == 2
    colors = set()
    for recipe in recipes:
        assert recipe["image"]
        media = api_client.get(f"/api/media/recipes/{recipe['id']}/images/original.webp")
        assert media.status_code == 200
        with Image.open(BytesIO(media.content)) as image:
            red, _, blue = image.convert("RGB").getpixel((20, 20))
            colors.add("red" if red > blue else "blue")
    assert colors == {"red", "blue"}


def test_corrupt_migration_image_is_reported(api_client: TestClient, unique_user_fn_scoped: TestUser) -> None:
    output = BytesIO()
    with ZipFile(BytesIO(archive_for("copymethat", True))) as source, ZipFile(output, "w") as target:
        for name in source.namelist():
            target.writestr(name, b"not an image" if name.endswith(".jpeg") else source.read(name))
    headers = unique_user_fn_scoped.token
    response = api_client.post(
        "/api/groups/migrations",
        data={"migration_type": "copymethat"},
        files={"archive": ("test.zip", output.getvalue(), "application/zip")},
        headers=headers,
    )
    assert response.status_code == 200
    report = api_client.get(f"/api/groups/reports/{response.json()['id']}", headers=headers).json()
    assert any(not entry["success"] and "image" in entry["message"] for entry in report["entries"])
    recipes = api_client.get("/api/recipes", headers=headers).json()["items"]
    assert len(recipes) == 1
    assert not recipes[0]["image"]
