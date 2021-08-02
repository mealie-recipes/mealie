from pathlib import Path

from pydantic2ts import generate_typescript_defs

CWD = Path(__file__).parent

PROJECT_DIR = Path(__file__).parent.parent.parent
SCHEMA_PATH = Path("/Users/hayden/Projects/Vue/mealie/mealie/schema/")

TYPES_DIR = CWD / "output" / "types" / "api-types"


def path_to_module(path: Path):
    path: str = str(path)

    path = path.removeprefix(str(PROJECT_DIR))
    path = path.removeprefix("/")
    path = path.replace("/", ".")

    return path


for module in SCHEMA_PATH.iterdir():

    if not module.is_dir() or not module.joinpath("__init__.py").is_file():
        continue

    ts_out_name = module.name.replace("_", "-") + ".ts"

    out_path = TYPES_DIR.joinpath(ts_out_name)

    print(module)
    try:
        path_as_module = path_to_module(module)
        generate_typescript_defs(path_as_module, str(out_path), exclude=("CamelModel"))
    except Exception:
        pass
