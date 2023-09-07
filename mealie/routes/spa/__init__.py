import pathlib

from fastapi import Depends, FastAPI, Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm.session import Session
from starlette.exceptions import HTTPException
from text_unidecode import os

from mealie.core.config import get_app_settings
from mealie.core.dependencies.dependencies import get_current_user
from mealie.db.db_setup import generate_session
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.user.user import PrivateUser

__app_settings = get_app_settings()


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


__contents = pathlib.Path(__app_settings.STATIC_FILES).joinpath("index.html").read_text()


async def serve_recipe_with_meta(
    slug: str,
    user: PrivateUser = Depends(get_current_user),
    session: Session = Depends(generate_session),
):
    repos = AllRepositories(session)

    recipe = repos.recipes.by_group(user.group_id).get_one(slug, "slug")
    if recipe is None:
        # Let SPA handle 404
        return Response(__contents, media_type="text/html", status_code=404)

    # Inject meta tags
    recipe_url = f"{__app_settings.BASE_URL}/recipe/{recipe.slug}"
    image_url = f"{__app_settings.BASE_URL}/api/media/recipes/{recipe.id}/images/original.webp?version={recipe.image}"

    tags = [
        f'<meta property="og:title" content="{recipe.name}" />',
        f'<meta property="og:description" content="{recipe.description}" />',
        f'<meta property="og:image" content="{image_url}" />',
        f'<meta property="og:url" content="{recipe_url}" />',
    ]

    contents = __contents.replace("</head>", "\n".join(tags) + "\n</head>", 1)

    # Serve contents as HTML
    return Response(contents, media_type="text/html")


def mount_spa(app: FastAPI):
    if not os.path.exists(__app_settings.STATIC_FILES):
        return

    app.get("/recipe/{slug}")(serve_recipe_with_meta)
    app.mount("/", SPAStaticFiles(directory=__app_settings.STATIC_FILES, html=True), name="spa")
