from fastapi import APIRouter, Depends
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.db.models.event import Event
from mealie.routes.deps import get_current_user
from mealie.schema.events import EventsOut
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/events", tags=["App Events"])


@router.get("", response_model=EventsOut)
async def get_events(session: Session = Depends(generate_session), current_user=Depends(get_current_user)):
    """ Get event from the Database """
    # Get Item
    return EventsOut(total=db.events.count_all(session), events=db.events.get_all(session, order_by="time_stamp"))


@router.delete("")
async def get_events(session: Session = Depends(generate_session), current_user=Depends(get_current_user)):
    """ Get event from the Database """
    # Get Item
    return db.events.delete_all(session)


@router.delete("/{id}")
async def delete_event(id: int, session: Session = Depends(generate_session), current_user=Depends(get_current_user)):
    """ Delete event from the Database """
    return db.events.delete(session, id)
