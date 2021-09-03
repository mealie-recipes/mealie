import json
import re
from dataclasses import dataclass
from pathlib import Path

from slugify import slugify

CWD = Path(__file__).parent

PROJECT_BASE = CWD.parent.parent

server_side_msgs = PROJECT_BASE / "mealie" / "utils" / "error_messages.py"
en_us_msgs = PROJECT_BASE / "frontend" / "lang" / "errors" / "en-US.json"
client_side_msgs = PROJECT_BASE / "frontend" / "utils" / "error-messages.ts"

GENERATE_MESSAGES = [
    # User Related
    "user",
    "webhook",
    "token",
    # Group Related
    "group",
    "cookbook",
    "mealplan",
    # Recipe Related
    "scraper",
    "recipe",
    "ingredient",
    "food",
    "unit",
    # Admin Related
    "backup",
    "migration",
    "event",
]


class ErrorMessage:
    def __init__(self, prefix, verb) -> None:
        self.message = f"{prefix.title()} {verb.title()} Failed"
        self.snake = slugify(self.message, separator="_")
        self.kabab = slugify(self.message, separator="-")

    def factory(prefix) -> list["ErrorMessage"]:
        verbs = ["Create", "Update", "Delete"]
        return [ErrorMessage(prefix, verb) for verb in verbs]


@dataclass
class CodeGenLines:
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
        self.text.insert(self._next_line, self.indentation + string)
        self._next_line += 1


def find_start(file_text: list[str], gen_id: str):
    for x, line in enumerate(file_text):
        if "CODE_GEN_ID:" in line and gen_id in line:
            return x, line

    return None


def find_end(file_text: list[str], gen_id: str):
    for x, line in enumerate(file_text):
        if f"END {gen_id}" in line:
            return x, line
    return None


def get_indentation_of_string(line: str):
    return re.sub(r"#.*", "", line).removesuffix("\n")


def get_messages(message_prefix: str) -> str:
    prefix = message_prefix.lower()

    return [
        f'{prefix}_create_failure = "{prefix}-create-failure"\n',
        f'{prefix}_update_failure = "{prefix}-update-failure"\n',
        f'{prefix}_delete_failure = "{prefix}-delete-failure"\n',
    ]


def code_gen_factory(file_path: Path) -> CodeGenLines:
    with open(file_path, "r") as file:
        text = file.readlines()
        start_num, line = find_start(text, "ERROR_MESSAGE_ENUMS")
        indentation = get_indentation_of_string(line)
        end_num, line = find_end(text, "ERROR_MESSAGE_ENUMS")

    return CodeGenLines(
        start=start_num,
        end=end_num,
        indentation=indentation,
        text=text,
    )


def write_to_locals(messages: list[ErrorMessage]) -> None:
    with open(en_us_msgs, "r") as f:
        existing_msg = json.loads(f.read())

    for msg in messages:
        if msg.kabab in existing_msg:
            continue

        existing_msg[msg.kabab] = msg.message
        print(f"Added Key {msg.kabab} to 'en-US.json'")

    with open(en_us_msgs, "w") as f:
        f.write(json.dumps(existing_msg, indent=4))


def main():
    print("Starting...")
    GENERATE_MESSAGES.sort()

    code_gen = code_gen_factory(server_side_msgs)
    code_gen.purge_lines()

    messages = []
    for msg_type in GENERATE_MESSAGES:
        messages += get_messages(msg_type)
        messages.append("\n")

    for msg in messages:
        code_gen.push_line(msg)

    with open(server_side_msgs, "w") as file:
        file.writelines(code_gen.text)

    # Locals

    local_msgs = []
    for msg_type in GENERATE_MESSAGES:
        local_msgs += ErrorMessage.factory(msg_type)

    write_to_locals(local_msgs)

    print("Done!")


if __name__ == "__main__":
    main()
