import json
from typing import Any

from _gen_utils import render_python_template
from _open_api_parser import OpenAPIParser
from _static import CodeDest, CodeTemplates
from rich.console import Console

from mealie.app import app

"""
This code is used for generating route objects for each route in the OpenAPI Specification.
Currently, they are NOT automatically injected into the test suite. As such, you'll need to copy
the relavent contents of the generated file into the test suite where applicable. I am slowly
migrating the test suite to use this new generated file and this process will be "automated" in the
future.
"""

console = Console()


def write_dict_to_file(file_name: str, data: dict[str, Any]):
    with open(file_name, "w") as f:
        f.write(json.dumps(data, indent=4))


def main():
    print("Starting...")
    open_api = OpenAPIParser(app)
    modules = open_api.get_by_module()

    mods = []

    for mod, value in modules.items():

        routes = []
        existings = set()
        # Reduce routes by unique py_route attribute
        for route in value:
            if route.py_route not in existings:
                existings.add(route.py_route)
                routes.append(route)

        module = {"name": mod, "routes": routes}
        mods.append(module)

    render_python_template(CodeTemplates.pytest_routes, CodeDest.pytest_routes, {"mods": mods})

    print("Finished...")


if __name__ == "__main__":
    main()
