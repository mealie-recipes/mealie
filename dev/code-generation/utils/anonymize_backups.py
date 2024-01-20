import json
import logging
import random
import string
from datetime import datetime
from uuid import UUID

logger = logging.getLogger("anonymize_backups")


def is_uuid4(value: str):
    try:
        UUID(value)
        return True
    except ValueError:
        return False


def is_iso_datetime(value: str):
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False


def random_string(length=10):
    return "".join(random.choice(string.ascii_lowercase) for _ in range(length))


def clean_value(value):
    try:
        match value:
            # preserve non-strings
            case int(value) | float(value):
                return value
            case None:
                return value
            # preserve UUIDs and datetimes
            case str(value) if is_uuid4(value) or is_iso_datetime(value):
                return value
            # randomize strings
            case str(value):
                return random_string()
            case _:
                pass

    except Exception as e:
        logger.exception(e)

    logger.error(f"Failed to anonymize value: {value}")
    return value


def walk_data_and_anonymize(data):
    for k, v in data.items():
        if isinstance(v, list):
            for item in v:
                walk_data_and_anonymize(item)
        else:
            # preserve alembic version number and enums
            if k in ["auth_method", "version_num"]:
                continue

            data[k] = clean_value(v)


def anonymize_database_json(input_filepath: str, output_filepath: str):
    with open(input_filepath) as f:
        data = json.load(f)

    walk_data_and_anonymize(data)
    with open(output_filepath, "w") as f:
        json.dump(data, f)
