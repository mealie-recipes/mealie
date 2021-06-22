from http.client import HTTPException

from fastapi import Depends, status
from mealie.core.root_logger import get_logger
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.routers import AdminAPIRouter
from mealie.schema.event_notifications import EventNotificationIn, EventNotificationOut
from mealie.schema.events import EventsOut, TestEvent
from mealie.services.events import test_notification
from sqlalchemy.orm.session import Session

router = AdminAPIRouter(prefix="/events", tags=["App Events"])

logger = get_logger()


@router.get("", response_model=EventsOut)
async def get_events(session: Session = Depends(generate_session)):
    """ Get event from the Database """
    # Get Item
    return EventsOut(total=db.events.count_all(session), events=db.events.get_all(session, order_by="time_stamp"))


@router.delete("")
async def delete_events(session: Session = Depends(generate_session)):
    """ Get event from the Database """
    # Get Item
    return db.events.delete_all(session)


@router.delete("/{id}")
async def delete_event(id: int, session: Session = Depends(generate_session)):
    """ Delete event from the Database """
    return db.events.delete(session, id)


@router.post("/notifications")
async def create_event_notification(
    event_data: EventNotificationIn,
    session: Session = Depends(generate_session),
):
    """ Create event_notification in the Database """

    return db.event_notifications.create(session, event_data)


@router.post("/notifications/test")
async def test_notification_route(
    test_data: TestEvent,
    session: Session = Depends(generate_session),
):
    """ Create event_notification in the Database """

    if test_data.id:
        event_obj: EventNotificationIn = db.event_notifications.get(session, test_data.id)
        test_data.test_url = event_obj.notification_url

    try:
        test_notification(test_data.test_url)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/notifications", response_model=list[EventNotificationOut])
async def get_all_event_notification(session: Session = Depends(generate_session)):
    """ Get all event_notification from the Database """
    # Get Item
    return db.event_notifications.get_all(session, override_schema=EventNotificationOut)


@router.put("/notifications/{id}")
async def update_event_notification(id: int, session: Session = Depends(generate_session)):
    """ Update event_notification in the Database """
    # not yet implemented
    raise HTTPException(status.HTTP_405_METHOD_NOT_ALLOWED)


@router.delete("/notifications/{id}")
async def delete_event_notification(id: int, session: Session = Depends(generate_session)):
    """ Delete event_notification from the Database """
    # Delete Item
    return db.event_notifications.delete(session, id)
