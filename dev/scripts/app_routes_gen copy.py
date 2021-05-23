import json
import re
from enum import Enum
from itertools import groupby
from pathlib import Path

import slugify
from fastapi import FastAPI
from humps import camelize
from jinja2 import Template
from mealie.app import app
from pydantic import BaseModel

CWD = Path(__file__).parent
OUT_DIR = CWD / "output"
OUT_FILE = OUT_DIR / "app_routes.py"

JS_DIR = OUT_DIR / "javascriptAPI"
JS_OUT_FILE = JS_DIR / "apiRoutes.js"
TEMPLATES_DIR = CWD / "templates"

PYTEST_TEMPLATE = TEMPLATES_DIR / "pytest_routes.j2"
JS_REQUESTS = TEMPLATES_DIR / "js_requests.j2"
JS_ROUTES = TEMPLATES_DIR / "js_routes.j2"
JS_INDEX = TEMPLATES_DIR / "js_index.j2"

JS_DIR.mkdir(exist_ok=True, parents=True)


class RouteObject:
    def __init__(self, route_string) -> None:
        self.prefix = "/" + route_string.split("/")[1]
        self.route = route_string.replace(self.prefix, "")
        self.js_route = self.route.replace("{", "${")
        self.parts = route_string.split("/")[1:]
        self.var = re.findall(r"\{(.*?)\}", route_string)
        self.is_function = "{" in self.route
        self.router_slug = slugify.slugify("_".join(self.parts[1:]), separator="_")
        self.router_camel = camelize(self.router_slug)

    def __repr__(self) -> str:
        return f"""Route: {self.route}
Parts: {self.parts}
Function: {self.is_function}
Var: {self.var}
Slug: {self.router_slug}
"""


class RequestType(str, Enum):
    get = "get"
    put = "put"
    post = "post"
    patch = "patch"
    delete = "delete"


class HTTPRequest(BaseModel):
    request_type: RequestType
    description: str = ""
    summary: str
    tags: list[str]

    @property
    def summary_camel(self):
        return camelize(self.summary)

    @property
    def js_docs(self):
        return self.description.replace("\n", "  \n  * ")


class PathObject(BaseModel):
    route_object: RouteObject
    http_verbs: list[HTTPRequest]

    class Config:
        arbitrary_types_allowed = True


def get_path_objects(app: FastAPI):
    paths = []

    with open("scratch.json", "w") as f:
        f.write(json.dumps(app.openapi()))
    for key, value in app.openapi().items():
        if key == "paths":
            for key, value in value.items():

                paths.append(
                    PathObject(
                        route_object=RouteObject(key),
                        http_verbs=[HTTPRequest(request_type=k, **v) for k, v in value.items()],
                    )
                )

    return paths


def read_template(file: Path):
    with open(file, "r") as f:
        return f.read()


def generate_template(app):
    paths = get_path_objects(app)

    static_paths = [x.route_object for x in paths if not x.route_object.is_function]
    function_paths = [x.route_object for x in paths if x.route_object.is_function]

    static_paths.sort(key=lambda x: x.router_slug)
    function_paths.sort(key=lambda x: x.router_slug)

    template = Template(read_template(PYTEST_TEMPLATE))
    content = template.render(paths={"prefix": "/api", "static_paths": static_paths, "function_paths": function_paths})
    with open(OUT_FILE, "w") as f:
        f.write(content)

    template = Template(read_template(JS_ROUTES))
    content = template.render(
        paths={"prefix": "/api", "static_paths": static_paths, "function_paths": function_paths, "all_paths": paths}
    )
    with open(JS_OUT_FILE, "w") as f:
        f.write(content)

    all_tags = []
    for k, g in groupby(paths, lambda x: x.http_verbs[0].tags[0]):
        template = Template(read_template(JS_REQUESTS))
        content = template.render(paths={"all_paths": list(g), "export_name": camelize(k)})

        all_tags.append(camelize(k))

        with open(JS_DIR.joinpath(camelize(k) + ".js"), "w") as f:
            f.write(content)

    template = Template(read_template(JS_INDEX))
    content = template.render(files={"files": all_tags})

    with open(JS_DIR.joinpath("index.js"), "w") as f:
        f.write(content)


if __name__ == "__main__":
    generate_template(app)
