import json
import pathlib
from dataclasses import dataclass

from bs4 import BeautifulSoup
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


@dataclass
class MetaTag:
    hid: str
    property_name: str
    content: str


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


def inject_meta(contents: str, tags: list[MetaTag]) -> str:
    soup = BeautifulSoup(contents, "lxml")
    scraped_meta_tags = soup.find_all("meta")

    tags_by_hid = {tag.hid: tag for tag in tags}
    for scraped_meta_tag in scraped_meta_tags:
        try:
            scraped_hid = scraped_meta_tag["data-hid"]
        except KeyError:
            continue

        if not (matched_tag := tags_by_hid.pop(scraped_hid, None)):
            continue

        scraped_meta_tag["property"] = matched_tag.property_name
        scraped_meta_tag["content"] = matched_tag.content

    # add any tags we didn't find
    if soup.html and soup.html.head:
        for tag in tags_by_hid.values():
            html_tag = soup.new_tag(
                "meta",
                **{"data-n-head": "1", "data-hid": tag.hid, "property": tag.property_name, "content": tag.content},
            )
            soup.html.head.append(html_tag)

    return str(soup)


def inject_recipe_json(contents: str, schema: dict) -> str:
    schema_as_html_tag = f"""<script type="application/ld+json">{json.dumps(jsonable_encoder(schema))}</script>"""
    return contents.replace("</head>", schema_as_html_tag + "\n</head>", 1)


def content_with_meta(group_slug: str, recipe: Recipe) -> str:
    # Inject meta tags
    recipe_url = f"{__app_settings.BASE_URL}/g/{group_slug}/r/{recipe.slug}"
    if recipe.image:
        image_url = (
            f"{__app_settings.BASE_URL}/api/media/recipes/{recipe.id}/images/original.webp?version={recipe.image}"
        )
    else:
        image_url = "https://raw.githubusercontent.com/mealie-recipes/mealie/9571816ac4eed5beacfc0abf6c03eff1427fd0eb/frontend/static/icons/android-chrome-512x512.png"

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

    nutrition: dict[str, str | None] = recipe.nutrition.model_dump(by_alias=True) if recipe.nutrition else {}

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
        "recipeYield": recipe.recipe_yield_display,
        "recipeIngredient": ingredients,
        "recipeInstructions": [i.text for i in recipe.recipe_instructions] if recipe.recipe_instructions else [],
        "recipeCategory": [c.name for c in recipe.recipe_category] if recipe.recipe_category else [],
        "keywords": [t.name for t in recipe.tags] if recipe.tags else [],
        "nutrition": nutrition,
    }

    meta_tags = [
        MetaTag(hid="og:title", property_name="og:title", content=recipe.name or ""),
        MetaTag(hid="og:description", property_name="og:description", content=recipe.description or ""),
        MetaTag(hid="og:image", property_name="og:image", content=image_url),
        MetaTag(hid="og:url", property_name="og:url", content=recipe_url),
        MetaTag(hid="twitter:card", property_name="twitter:card", content="summary_large_image"),
        MetaTag(hid="twitter:title", property_name="twitter:title", content=recipe.name or ""),
        MetaTag(hid="twitter:description", property_name="twitter:description", content=recipe.description or ""),
        MetaTag(hid="twitter:image", property_name="twitter:image", content=image_url),
        MetaTag(hid="twitter:url", property_name="twitter:url", content=recipe_url),
    ]

    global __contents
    contents = __contents  # make a local copy so we don't modify the global contents
    contents = inject_recipe_json(contents, as_schema_org)
    contents = inject_meta(contents, meta_tags)

    return contents


def response_404():
    return Response(__contents, media_type="text/html", status_code=404)


def serve_recipe_with_meta_public(
    group_slug: str,
    recipe_slug: str,
    session: Session = Depends(generate_session),
):
    try:
        public_repos = AllRepositories(session)
        group = public_repos.groups.get_by_slug_or_id(group_slug)

        if not (group and group.preferences) or group.preferences.private_group:
            return response_404()

        group_repos = AllRepositories(session, group_id=group.id, household_id=None)
        recipe = group_repos.recipes.get_one(recipe_slug)

        if not (recipe and recipe.settings) or not recipe.settings.public:
            return response_404()

        # Inject meta tags
        return Response(content_with_meta(group_slug, recipe), media_type="text/html")
    except Exception:
        return response_404()


async def serve_recipe_with_meta(
    group_slug: str,
    recipe_slug: str,
    user: PrivateUser | None = Depends(try_get_current_user),
    session: Session = Depends(generate_session),
):
    if not user or user.group_slug != group_slug:
        return serve_recipe_with_meta_public(group_slug, recipe_slug, session)

    try:
        group_repos = AllRepositories(session, group_id=user.group_id, household_id=None)

        recipe = group_repos.recipes.get_one(recipe_slug, "slug")
        if recipe is None:
            return response_404()

        # Serve contents as HTML
        return Response(content_with_meta(group_slug, recipe), media_type="text/html")
    except Exception:
        return response_404()


async def serve_shared_recipe_with_meta(group_slug: str, token_id: str, session: Session = Depends(generate_session)):
    try:
        public_repos = AllRepositories(session, group_id=None)
        token_summary = public_repos.recipe_share_tokens.get_one(token_id)
        if token_summary is None:
            raise Exception("Token Not Found")

        return Response(content_with_meta(group_slug, token_summary.recipe), media_type="text/html")

    except Exception:
        return response_404()


def mount_spa(app: FastAPI):
    if not os.path.exists(__app_settings.STATIC_FILES):
        return

    global __contents
    __contents = pathlib.Path(__app_settings.STATIC_FILES).joinpath("index.html").read_text()

    app.get("/g/{group_slug}/r/{recipe_slug}", include_in_schema=False)(serve_recipe_with_meta)
    app.get("/g/{group_slug}/shared/r/{token_id}", include_in_schema=False)(serve_shared_recipe_with_meta)
    app.mount("/", SPAStaticFiles(directory=__app_settings.STATIC_FILES, html=True), name="spa")
