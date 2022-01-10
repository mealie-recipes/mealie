from fastapi import Depends

from mealie.repos.all_repositories import generate_repositories
from mealie.repos.repository_factory import AllRepositories
from mealie.routes._base.controller import controller
from mealie.routes.routers import AdminAPIRouter
from mealie.schema.events import EventsOut

router = AdminAPIRouter(prefix="/events")


@controller(router)
class EventsController:
    repos: AllRepositories = Depends(generate_repositories)

    @router.get("", response_model=EventsOut)
    async def get_events(self):
        """Get event from the Database"""

        return EventsOut(total=self.repos.events.count_all(), events=self.repos.events.get_all(order_by="time_stamp"))

    @router.delete("")
    async def delete_events(self):
        """Get event from the Database"""
        self.repos.events.delete_all()
        return {"message": "All events deleted"}

    @router.delete("/{id}")
    async def delete_event(self, id: int):
        """Delete event from the Database"""
        return self.repos.events.delete(id)
