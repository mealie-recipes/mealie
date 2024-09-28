from pydantic import UUID4
from sqlalchemy.orm import Session

from ._utils import NOT_SET, NotSet
from .repository_factory import AllRepositories


def get_repositories(
    session: Session, *, group_id: UUID4 | None | NotSet = NOT_SET, household_id: UUID4 | None | NotSet = NOT_SET
):
    return AllRepositories(session, group_id=group_id, household_id=household_id)
