import json
import re
from pathlib import Path

import slugify
from jinja2 import Template
from mealie.app import app

CWD = Path(__file__).parent
OUT_FILE = CWD.joinpath("output", "app_routes.py")

code_template = """
class AppRoutes:
    def __init__(self) -> None:
        self.prefix = '{{paths.prefix}}'
{% for path in paths.static_paths %}
        self.{{ path.router_slug }} = "{{path.prefix}}{{ path.route }}"{% endfor %}
{% for path in paths.function_paths  %}
    def {{path.router_slug}}(self, {{path.var|join(", ")}}):
        return f"{self.prefix}{{ path.route }}"
{% endfor %}
"""


def get_variables(path):
    path = path.replace("/", " ")
    print(path)
    var = re.findall(r" \{.*\}", path)
    print(var)
    if var:
        return [v.replace("{", "").replace("}", "") for v in var]
    else:
        return None


class RouteObject:
    def __init__(self, route_string) -> None:
        self.prefix = "/" + route_string.split("/")[1]
        self.route = route_string.replace(self.prefix, "")
        self.parts = route_string.split("/")[1:]
        self.var = re.findall(r"\{(.*?)\}", route_string)
        self.is_function = "{" in self.route
        self.router_slug = slugify.slugify("_".join(self.parts[1:]), separator="_")

    def __repr__(self) -> str:
        return f"""Route: {self.route}
Parts: {self.parts}
Function: {self.is_function}
Var: {self.var}
Slug: {self.router_slug}
"""


def get_paths(app):
    paths = []
    print(json.dumps(app.openapi()))
    for key, value in app.openapi().items():
        if key == "paths":
            for key, value in value.items():
                paths.append(key)

    return paths


def generate_template(app):
    paths = get_paths(app)
    new_paths = [RouteObject(path) for path in paths]

    static_paths = [p for p in new_paths if not p.is_function]
    function_paths = [p for p in new_paths if p.is_function]

    template = Template(code_template)

    content = template.render(paths={"prefix": "/api", "static_paths": static_paths, "function_paths": function_paths})

    with open(OUT_FILE, "w") as f:
        f.write(content)


if __name__ == "__main__":
    generate_template(app)
