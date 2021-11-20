import json
import re
from enum import Enum
from itertools import groupby
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from humps import camelize
from jinja2 import Template
from pydantic import BaseModel, Field
from slugify import slugify

from mealie.app import app

CWD = Path(__file__).parent
OUT_DIR = CWD / "output"
TEMPLATES_DIR = CWD / "templates"

JS_DIR = OUT_DIR / "javascriptAPI"
JS_DIR.mkdir(exist_ok=True, parents=True)


class RouteObject:
    def __init__(self, route_string) -> None:
        self.prefix = "/" + route_string.split("/")[1]
        self.route = "/" + route_string.split("/", 2)[2]
        self.js_route = self.route.replace("{", "${")
        self.parts = route_string.split("/")[1:]
        self.var = re.findall(r"\{(.*?)\}", route_string)
        self.is_function = "{" in self.route
        self.router_slug = slugify("_".join(self.parts[1:]), separator="_")
        self.router_camel = camelize(self.router_slug)


class RequestType(str, Enum):
    get = "get"
    put = "put"
    post = "post"
    patch = "patch"
    delete = "delete"


class ParameterIn(str, Enum):
    query = "query"
    path = "path"


class RouterParameter(BaseModel):
    required: bool = False
    name: str
    location: ParameterIn = Field(..., alias="in")


class RequestBody(BaseModel):
    required: bool = False


class HTTPRequest(BaseModel):
    request_type: RequestType
    description: str = ""
    summary: str
    requestBody: Optional[RequestBody]

    parameters: list[RouterParameter] = []
    tags: list[str]

    def list_as_js_object_string(self, parameters, braces=True):
        if len(parameters) == 0:
            return ""

        if braces:
            return "{" + ", ".join(parameters) + "}"
        else:
            return ", ".join(parameters)

    def payload(self):
        return "payload" if self.requestBody else ""

    def function_args(self):
        all_params = [p.name for p in self.parameters]
        if self.requestBody:
            all_params.append("payload")
        return self.list_as_js_object_string(all_params)

    def query_params(self):
        params = [param.name for param in self.parameters if param.location == ParameterIn.query]
        return self.list_as_js_object_string(params)

    def path_params(self):
        params = [param.name for param in self.parameters if param.location == ParameterIn.path]
        return self.list_as_js_object_string(parameters=params, braces=False)

    @property
    def summary_camel(self):
        return camelize(slugify(self.summary))

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


def dump_open_api(app: FastAPI):
    """Writes the Open API as JSON to a json file"""
    OPEN_API_FILE = CWD / "openapi.json"

    with open(OPEN_API_FILE, "w") as f:
        f.write(json.dumps(app.openapi()))


def read_template(file: Path):
    with open(file, "r") as f:
        return f.read()


def generate_python_templates(static_paths: list[PathObject], function_paths: list[PathObject]):
    PYTEST_TEMPLATE = TEMPLATES_DIR / "pytest_routes.j2"
    PYTHON_OUT_FILE = OUT_DIR / "app_routes.py"

    template = Template(read_template(PYTEST_TEMPLATE))
    content = template.render(
        paths={
            "prefix": "/api",
            "static_paths": static_paths,
            "function_paths": function_paths,
        }
    )
    with open(PYTHON_OUT_FILE, "w") as f:
        f.write(content)

    return


def generate_js_templates(paths: list[PathObject]):
    # Template Path
    JS_API_INTERFACE = TEMPLATES_DIR / "js_api_interface.j2"
    JS_INDEX = TEMPLATES_DIR / "js_index.j2"

    INTERFACES_DIR = JS_DIR / "interfaces"
    INTERFACES_DIR.mkdir(exist_ok=True, parents=True)

    all_tags = []
    for tag, tag_paths in groupby(paths, lambda x: x.http_verbs[0].tags[0]):
        file_name = slugify(tag, separator="-")

        tag = camelize(tag)

        tag_paths: list[PathObject] = list(tag_paths)

        template = Template(read_template(JS_API_INTERFACE))
        content = template.render(
            paths={
                "prefix": "/api",
                "static_paths": [x.route_object for x in tag_paths if not x.route_object.is_function],
                "function_paths": [x.route_object for x in tag_paths if x.route_object.is_function],
                "all_paths": tag_paths,
                "export_name": tag,
            }
        )

        tag: dict = {"camel": camelize(tag), "slug": file_name}
        all_tags.append(tag)

        with open(INTERFACES_DIR.joinpath(file_name + ".ts"), "w") as f:
            f.write(content)

    template = Template(read_template(JS_INDEX))
    content = template.render(files={"files": all_tags})

    with open(JS_DIR.joinpath("index.js"), "w") as f:
        f.write(content)


def generate_template(app):
    dump_open_api(app)
    paths = get_path_objects(app)

    static_paths = [x.route_object for x in paths if not x.route_object.is_function]
    function_paths = [x.route_object for x in paths if x.route_object.is_function]

    static_paths.sort(key=lambda x: x.router_slug)
    function_paths.sort(key=lambda x: x.router_slug)

    generate_python_templates(static_paths, function_paths)
    generate_js_templates(paths)


if __name__ == "__main__":
    generate_template(app)
