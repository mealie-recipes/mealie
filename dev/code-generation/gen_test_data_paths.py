from dataclasses import dataclass
from pathlib import Path

from _gen_utils import render_python_template
from slugify import slugify

CWD = Path(__file__).parent

TEMPLATE = CWD / "templates" / "test_data.py.j2"

TEST_DATA = CWD.parent.parent / "tests" / "data"

GENERATED = CWD / "generated"


@dataclass
class TestDataPath:
    var: str
    path: str

    @classmethod
    def from_path(cls, path: Path):
        var = str(path)
        var = var.replace(str(TEST_DATA), "")

        rel_path = var.removeprefix("/")

        # Remove any file extension
        var = var.split(".")[0]

        var = var.replace("'", "")

        var = slugify(var, separator="_")

        return cls(var, rel_path)


@dataclass
class DataDir:
    name: str
    path: Path
    children: list[TestDataPath]


def get_data_paths(path: Path) -> list[DataDir]:
    """
    Recursively walks the given path and returns a list of TestDataPaths
    """

    def recursive_test_paths(p: Path) -> list[TestDataPath]:
        test_paths = []
        for child in p.iterdir():
            if child.is_dir():
                test_paths += recursive_test_paths(child)
            else:
                test_paths.append(TestDataPath.from_path(child))
        return [x for x in test_paths if not None]

    data_paths = []

    for p in path.iterdir():
        if p.is_dir():
            data_paths.append(DataDir(p.name, p, recursive_test_paths(p)))

    return data_paths


def rename_non_compliant_paths():
    """
    Recursively itterates through a directory and renames all files/folders to be
    kabab case.
    """

    ignore_files = ["DS_Store", ".gitkeep"]

    ignore_extensions = [".pyc", ".pyo", ".py"]

    def recursive_rename(p: Path):
        for child in p.iterdir():
            if str(child).startswith("."):
                continue

            if child.suffix in ignore_extensions:
                continue

            if child.name in ignore_files:
                continue

            if child.is_dir():
                recursive_rename(child)

            else:
                new_name = slugify(child.stem)
                extension = child.suffix
                if new_name != child.name:
                    child.rename(child.parent / f"{new_name}{extension}")

    recursive_rename(TEST_DATA)


def main():
    print("Starting Template Generation")

    rename_non_compliant_paths()

    GENERATED.mkdir(exist_ok=True)
    data_dirs = get_data_paths(TEST_DATA)

    all_children = [x.children for x in data_dirs]

    # Flatten list of lists
    all_children = [item for sublist in all_children for item in sublist]

    render_python_template(
        TEMPLATE,
        GENERATED / "__init__.py",
        {"children": all_children},
    )

    print("Finished Template Generation")


if __name__ == "__main__":
    main()
