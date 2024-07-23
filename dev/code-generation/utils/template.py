import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Template
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()])

log = logging.getLogger("rich")


def render_python_template(template_file: Path | str, dest: Path, data: dict):
    """Render and Format a Jinja2 Template for Python Code"""
    if isinstance(template_file, Path):
        tplt = Template(template_file.read_text())
    else:
        tplt = Template(template_file)

    text = tplt.render(data=data)

    dest.write_text(text)

    # lint/format file with Ruff
    log.info(f"Formatting {dest}")
    subprocess.run(["poetry", "run", "ruff", "check", str(dest), "--fix"])
    subprocess.run(["poetry", "run", "ruff", "format", str(dest)])


@dataclass
class CodeSlicer:
    start: int
    end: int

    indentation: str
    text: list[str]

    _next_line = None

    def purge_lines(self) -> None:
        start = self.start + 1
        end = self.end
        del self.text[start:end]

    def push_line(self, string: str) -> None:
        self._next_line = self._next_line or self.start + 1
        self.text.insert(self._next_line, self.indentation + string + "\n")
        self._next_line += 1


def get_indentation_of_string(line: str, comment_char: str = "//|#") -> str:
    return re.sub(rf"{comment_char}.*", "", line).removesuffix("\n")


def find_start_end(file_text: list[str], gen_id: str) -> tuple[int, int, str]:
    start = None
    end = None
    indentation = None

    for i, line in enumerate(file_text):
        if "CODE_GEN_ID:" in line and gen_id in line:
            start = i
            indentation = get_indentation_of_string(line)
        if f"END: {gen_id}" in line:
            end = i

    if start is None or end is None:
        raise Exception("Could not find start and end of code generation block")

    if start > end:
        raise Exception(f"Start ({start=}) of code generation block is after end ({end=})")

    return start, end, indentation


def inject_inline(file_path: Path, key: str, code: list[str]) -> None:
    """Injects a list of strings into the file where the key is found in the format defined
    by the code-generation. Strings are properly indented and a '\n' is added to the end of
    each string.

    Start -> 'CODE_GEN_ID: <key>'
    End -> 'END: <key>'

    If no 'CODE_GEN_ID: <key>' is found, and exception is raised

    Args:
        file_path (Path): Write to file
        key (str): CODE_GEN_ID: <key>
        code (list[str]): List of strings to inject.

    """

    with open(file_path) as f:
        file_text = f.readlines()

    start, end, indentation = find_start_end(file_text, key)

    slicer = CodeSlicer(start, end, indentation, file_text)

    slicer.purge_lines()

    for line in code:
        slicer.push_line(line)

    with open(file_path, "w") as file:
        file.writelines(slicer.text)
