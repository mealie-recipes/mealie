from _gen_utils import log, render_python_template
from _static import PROJECT_DIR

template = """# GENERATED CODE - DO NOT MODIFY BY HAND
{% for file in data.files %}from .{{ file }} import *
{% endfor %}
"""

SCHEMA_PATH = PROJECT_DIR / "mealie" / "schema"


def generate_init_files() -> None:
    for schema in SCHEMA_PATH.iterdir():
        if not schema.is_dir():
            log.info(f"Skipping {schema}")
            continue

        log.info(f"Generating {schema}")
        init_file = schema.joinpath("__init__.py")

        module_files = [
            f.stem for f in schema.iterdir() if f.is_file() and f.suffix == ".py" and not f.stem.startswith("_")
        ]
        render_python_template(template, init_file, {"files": module_files})


def main():
    log.info("Starting...")
    generate_init_files()
    log.info("Finished...")


if __name__ == "__main__":
    main()
