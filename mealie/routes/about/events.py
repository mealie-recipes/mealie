from mealie.routes.routers import AdminAPIRouter
from mealie.schema.events import EventsOut

from .._base import BaseAdminController, controller

router = AdminAPIRouter(prefix="/events")


@controller(router)
class EventsController(BaseAdminController):
    @router.get("", response_model=EventsOut)
    async def get_events(self):
        """Get event from the Database"""
        return EventsOut(total=self.repos.events.count_all(), events=self.repos.events.get_all(order_by="time_stamp"))

    @router.delete("")
    async def delete_events(self):
        """Get event from the Database"""
        self.repos.events.delete_all()
        return {"message": "All events deleted"}

    @router.delete("/{item_id}")
    async def delete_event(self, item_id: int):
        """Delete event from the Database"""
        return self.repos.events.delete(item_id)
