import json
from pathlib import Path

from fastapi import FastAPI
from jinja2 import Template
from pydantic import BaseModel
from utils import PROJECT_DIR, CodeTemplates, HTTPRequest, RouteObject

CWD = Path(__file__).parent

OUTFILE = PROJECT_DIR / "tests" / "utils" / "api_routes" / "__init__.py"


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
    with open(file) as f:
        return f.read()


def generate_python_templates(static_paths: list[PathObject], function_paths: list[PathObject]):

    template = Template(read_template(CodeTemplates.pytest_routes))
    content = template.render(
        paths={
            "prefix": "/api",
            "static_paths": static_paths,
            "function_paths": function_paths,
        }
    )
    with open(OUTFILE, "w") as f:
        f.write(content)

    return


def main():
    from mealie.app import app

    dump_open_api(app)
    paths = get_path_objects(app)

    static_paths = [x.route_object for x in paths if not x.route_object.is_function]
    function_paths = [x.route_object for x in paths if x.route_object.is_function]

    static_paths.sort(key=lambda x: x.router_slug)
    function_paths.sort(key=lambda x: x.router_slug)

    generate_python_templates(static_paths, function_paths)


if __name__ == "__main__":
    main()
