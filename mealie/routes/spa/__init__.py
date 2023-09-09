import json
import pathlib

from fastapi import Depends, FastAPI, Response
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm.session import Session
from starlette.exceptions import HTTPException
from text_unidecode import os

from mealie.core.config import get_app_settings
from mealie.core.dependencies.dependencies import try_get_current_user
from mealie.db.db_setup import generate_session
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.user.user import PrivateUser


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex
        except Exception as e:
            raise e


__app_settings = get_app_settings()
__contents = ""


def content_with_meta(recipe: Recipe) -> str:
    # Inject meta tags
    recipe_url = f"{__app_settings.BASE_URL}/recipe/{recipe.slug}"
    image_url = f"{__app_settings.BASE_URL}/api/media/recipes/{recipe.id}/images/original.webp?version={recipe.image}"

    ingredients: list[str] = []
    if recipe.settings.disable_amount:  # type: ignore
        ingredients = [i.note for i in recipe.recipe_ingredient if i.note]

    else:
        for ing in recipe.recipe_ingredient:
            s = ""
            if ing.quantity:
                s += f"{ing.quantity} "
            if ing.unit:
                s += f"{ing.unit.name} "
            if ing.food:
                s += f"{ing.food.name} "
            if ing.note:
                s += f"{ing.note}"

            ingredients.append(s)

    nutrition: dict[str, str | None] = {}
    if recipe.nutrition:
        nutrition["calories"] = recipe.nutrition.calories
        nutrition["fatContent"] = recipe.nutrition.fat_content
        nutrition["fiberContent"] = recipe.nutrition.fiber_content
        nutrition["proteinContent"] = recipe.nutrition.protein_content
        nutrition["carbohydrateContent"] = recipe.nutrition.carbohydrate_content
        nutrition["sodiumContent"] = recipe.nutrition.sodium_content
        nutrition["sugarContent"] = recipe.nutrition.sugar_content

    as_schema_org = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": recipe.name,
        "description": recipe.description,
        "image": [image_url],
        "datePublished": recipe.created_at,
        "prepTime": recipe.prep_time,
        "cookTime": recipe.cook_time,
        "totalTime": recipe.total_time,
        "recipeYield": recipe.recipe_yield,
        "recipeIngredient": ingredients,
        "recipeInstructions": [i.text for i in recipe.recipe_instructions] if recipe.recipe_instructions else [],
        "recipeCategory": [c.name for c in recipe.recipe_category] if recipe.recipe_category else [],
        "keywords": [t.name for t in recipe.tags] if recipe.tags else [],
        "nutrition": nutrition,
    }

    tags = [
        f'<meta property="og:title" content="{recipe.name}" />',
        f'<meta property="og:description" content="{recipe.description}" />',
        f'<meta property="og:image" content="{image_url}" />',
        f'<meta property="og:url" content="{recipe_url}" />',
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{recipe.name}" />',
        f'<meta name="twitter:description" content="{recipe.description}" />',
        f'<meta name="twitter:image" content="{image_url}" />',
        f'<meta name="twitter:url" content="{recipe_url}" />',
        f"""<script type="application/ld+json">{json.dumps(jsonable_encoder(as_schema_org))}</script>""",
    ]

    return __contents.replace("</head>", "\n".join(tags) + "\n</head>", 1)


def response_404():
    return Response(__contents, media_type="text/html", status_code=404)


def serve_recipe_with_meta_public(
    group_slug: str,
    recipe_slug: str,
    session: Session = Depends(generate_session),
):
    try:
        repos = AllRepositories(session)
        group = repos.groups.get_by_slug_or_id(group_slug)

        if not group or group.preferences.private_group:  # type: ignore
            return response_404()

        recipe = repos.recipes.by_group(group.id).get_one(recipe_slug)

        if not recipe or not recipe.settings.public:  # type: ignore
            return response_404()

        # Inject meta tags
        return Response(content_with_meta(recipe), media_type="text/html")
    except Exception:
        return response_404()


async def serve_recipe_with_meta(
    slug: str,
    user: PrivateUser = Depends(try_get_current_user),
    session: Session = Depends(generate_session),
):
    if not user:
        return Response(__contents, media_type="text/html", status_code=401)

    try:
        repos = AllRepositories(session)

        recipe = repos.recipes.by_group(user.group_id).get_one(slug, "slug")
        if recipe is None:
            return response_404()

        # Serve contents as HTML
        return Response(content_with_meta(recipe), media_type="text/html")
    except Exception:
        return response_404()


def mount_spa(app: FastAPI):
    if not os.path.exists(__app_settings.STATIC_FILES):
        return

    global __contents
    __contents = pathlib.Path(__app_settings.STATIC_FILES).joinpath("index.html").read_text()

    app.get("/recipe/{slug}")(serve_recipe_with_meta)
    app.get("/explore/recipes/{group_slug}/{recipe_slug}")(serve_recipe_with_meta_public)
    app.mount("/", SPAStaticFiles(directory=__app_settings.STATIC_FILES, html=True), name="spa")
