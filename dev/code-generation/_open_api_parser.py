import json
import re
from pathlib import Path
from typing import Any

from _static import Directories
from fastapi import FastAPI
from humps import camelize
from slugify import slugify


def get_openapi_spec_by_ref(app, type_reference: str) -> dict:
    if not type_reference:
        return None

    schemas = app["components"]["schemas"]
    type_text = type_reference.split("/")[-1]
    return schemas.get(type_text, type_reference)


def recursive_dict_search(data: dict[str, Any], key: str) -> Any:
    """
    Walks a dictionary searching for a key and returns all the keys
    matching the provided key"""
    if key in data:
        return data[key]
    for _, v in data.items():
        if isinstance(v, dict):
            result = recursive_dict_search(v, key)
            if result:
                return result
    return None


class APIFunction:
    def __init__(self, app, route: str, verb: str, data: dict):
        self.name_camel = camelize(data.get("summary"))
        self.name_snake = slugify(data.get("summary"), separator="_")

        self.http_verb = verb
        self.path_vars = re.findall(r"\{(.*?)\}", route)
        self.path_is_func = "{" in route
        self.js_route = route.replace("{", "${")
        self.py_route = route

        self.body_schema = get_openapi_spec_by_ref(app, recursive_dict_search(data, "$ref"))

    def path_args(self) -> str:
        return ", ".join(x + ": string | number" for x in self.path_vars)

    # body: Optional[list[str]] = []
    # path_params: Optional[list[str]] = []
    # query_params: Optional[list[str]] = []


# class APIModule(BaseModel):
#     name: str
#     functions: list[APIFunction]


class OpenAPIParser:
    def __init__(self, app: FastAPI) -> None:
        self.app = app
        self.spec = app.openapi()

        self.modules = {}

    def dump(self, out_path: Path) -> Path:
        """ Writes the Open API as JSON to a json file"""
        OPEN_API_FILE = out_path or Directories.out_dir / "openapi.json"

        with open(OPEN_API_FILE, "w") as f:
            f.write(json.dumps(self.spec, indent=4))

    def _group_by_module_tag(self):
        """
        Itterates over all routes and groups them by module. Modules are determined
        by the suffix text before : in the first tag for the router. These are used
        to generate the typescript class interface for interacting with the API
        """
        modules = {}

        all_paths = self.spec["paths"]
        for path, http_verbs in all_paths.items():
            for _, value in http_verbs.items():
                if "tags" in value:
                    tag: str = value["tags"][0]
                    if ":" in tag:
                        tag = tag.removeprefix('"').split(":")[0].replace(" ", "")
                        if modules.get(tag):
                            modules[tag][path] = http_verbs
                        else:
                            modules[tag] = {path: http_verbs}

        return modules

    def _get_openapi_spec(self, type_reference: str) -> dict:
        schemas = self.app["components"]["schemas"]
        type_text = type_reference.split("/")[-1]
        return schemas.get(type_text, type_reference)

    def _fill_schema_references(self, raw_modules: dict) -> dict:
        for _, routes in raw_modules.items():
            for _, verbs in routes.items():
                for _, value in verbs.items():
                    if "requestBody" in value:
                        try:
                            schema_ref = value["requestBody"]["content"]["application/json"]["schema"]["$ref"]
                            schema = self._get_openapi_spec(schema_ref)
                            value["requestBody"]["content"]["application/json"]["schema"] = schema
                        except Exception:
                            continue

        return raw_modules

    def get_by_module(self) -> dict:
        """Returns paths where tags are split by : and left right is considered the module"""
        raw_modules = self._group_by_module_tag()

        modules = {}
        for module_name, routes in raw_modules.items():
            for route, verbs in routes.items():
                for verb, value in verbs.items():
                    function = APIFunction(self.spec, route, verb, value)

                    if modules.get(module_name):
                        modules[module_name].append(function)
                    else:
                        modules[module_name] = [function]

        return modules
