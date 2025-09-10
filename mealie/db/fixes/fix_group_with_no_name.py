from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mealie.core import root_logger
from mealie.db.models.group import Group

logger = root_logger.get_logger("init_db")


def _do_fix(session: Session, group: Group, counter: int):
    if counter:
        new_name = f"{group.id} ({counter})"
    else:
        new_name = str(group.id)

    group.name = new_name
    group.slug = slugify(group.name)
    session.commit()


def fix_group_with_no_name(session: Session):
    groups = session.query(Group).filter(Group.name == "").all()
    if not groups:
        logger.debug("No group found with an empty name; skipping fix")
        return

    logger.info(
        f"{len(groups)} {'group' if len(groups) == 1 else 'groups'} found with a missing name; applying default name"
    )

    offset = 0
    for i, group in enumerate(groups):
        attempts = 0
        while True:
            if attempts >= 3:
                raise Exception(
                    f'Unable to fix empty group name for group_id "{group.id}": too many attempts ({attempts})'
                )

            counter = i + offset
            try:
                _do_fix(session, group, counter)
                break
            except IntegrityError:
                session.rollback()
                attempts += 1
                offset += 1
                continue
