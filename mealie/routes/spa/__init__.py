import pathlib

from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from text_unidecode import os

from mealie.core.config import get_app_settings

__static_path = get_app_settings().STATIC_FILES


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


async def serve_recipe_with_meta(slug: str):
    # TODO: Inject Tags and other meta data

    # Inject meta tags
    tags = [
        f'<meta property="og:title" content="{slug}" />',
    ]

    contents = pathlib.Path(__static_path).joinpath("index.html").read_text()
    contents = contents.replace("</head>", "\n".join(tags) + "\n</head>", 1)

    # Serve contents as HTML
    return Response(contents, media_type="text/html")


def mount_spa(app: FastAPI):
    if not os.path.exists(__static_path):
        return

    app.route("/recipe/{slug}")(serve_recipe_with_meta)
    app.mount("/", SPAStaticFiles(directory=__static_path, html=True), name="spa")
