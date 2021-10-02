from fastapi import Depends
from sqlalchemy.orm.session import Session

from mealie.core.root_logger import get_logger
from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.routes.routers import AdminAPIRouter
from mealie.schema.events import EventsOut

router = AdminAPIRouter(prefix="/events")

logger = get_logger()


@router.get("", response_model=EventsOut)
async def get_events(session: Session = Depends(generate_session)):
    """ Get event from the Database """
    db = get_database(session)

    return EventsOut(total=db.events.count_all(), events=db.events.get_all(order_by="time_stamp"))


@router.delete("")
async def delete_events(session: Session = Depends(generate_session)):
    """ Get event from the Database """
    db = get_database(session)
    return db.events.delete_all()


@router.delete("/{id}")
async def delete_event(id: int, session: Session = Depends(generate_session)):
    """ Delete event from the Database """
    db = get_database(session)
    return db.events.delete(id)
