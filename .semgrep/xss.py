# Test cases for xss.yml. Run with `mise run py:semgrep`.
import json

import jinja2
from fastapi import Response
from fastapi.responses import HTMLResponse
from jinja2 import Environment, Template
from markupsafe import Markup

from mealie.routes.spa import script_safe_json


def templates(source: str):
    # ruleid: mealie-jinja-autoescape
    Template(source)

    # ruleid: mealie-jinja-autoescape
    jinja2.Environment(loader=None)

    # ruleid: mealie-jinja-autoescape
    Template(source, autoescape=False)

    # ok: mealie-jinja-autoescape
    Template(source, autoescape=True)

    # ok: mealie-jinja-autoescape
    Environment(loader=None, autoescape=True)


def script_tags(schema: dict, name: str):
    # ruleid: mealie-script-tag-json
    a = f"""<script type="application/ld+json">{json.dumps(schema)}</script>"""

    # ruleid: mealie-script-tag-json
    b = f"<script>var name = {name};</script>"

    # ok: mealie-script-tag-json
    c = f"""<script type="application/ld+json">{script_safe_json(schema)}</script>"""

    return a, b, c


def responses(name: str):
    # ruleid: mealie-html-response-fstring
    HTMLResponse(f"<h1>{name}</h1>")

    # ruleid: mealie-html-response-fstring
    Response(f"<h1>{name}</h1>", media_type="text/html")

    # ruleid: mealie-html-response-fstring
    Markup(f"<b>{name}</b>")

    # ok: mealie-html-response-fstring
    Response(f'{{"name": "{name}"}}', media_type="application/json")
