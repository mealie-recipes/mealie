from fastapi import APIRouter

from mealie.core.root_logger import LOGGER_FILE
from mealie.core.security import create_file_token

router = APIRouter(prefix="/logs")


@router.get("/{num}")
async def get_log(num: int):
    """Doc Str"""
    with open(LOGGER_FILE, "rb") as f:
        log_text = tail(f, num)
    return log_text


@router.get("")
async def get_log_file():
    """Returns a token to download a file"""
    return {"fileToken": create_file_token(LOGGER_FILE)}


def tail(f, lines=20):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    while lines_to_go > 0 and block_end_byte > 0:
        if block_end_byte - BLOCK_SIZE > 0:
            f.seek(block_number * BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            f.seek(0, 0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b"\n")
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = b"".join(reversed(blocks))
    return b"/n".join(all_read_text.splitlines()[-total_lines_wanted:])
