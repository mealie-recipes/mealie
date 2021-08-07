import { BaseAPI } from "./_base";

export type EventCategory = "general" | "recipe" | "backup" | "scheduled" | "migration" | "group" | "user";

export interface Event {
  id?: number;
  title: string;
  text: string;
  timeStamp?: string;
  category?: EventCategory & string;
}

export interface EventsOut {
  total: number;
  events: Event[];
}

const prefix = "/api";

const routes = {
  aboutEvents: `${prefix}/about/events`,
  aboutEventsNotifications: `${prefix}/about/events/notifications`,
  aboutEventsNotificationsTest: `${prefix}/about/events/notifications/test`,

  aboutEventsId: (id: number) => `${prefix}/about/events/${id}`,
  aboutEventsNotificationsId: (id: number) => `${prefix}/about/events/notifications/${id}`,
};

export class EventsAPI extends BaseAPI {
  /** Get event from the Database
   */
  async getEvents() {
    return await this.requests.get<EventsOut>(routes.aboutEvents);
  }

  /** Get event from the Database
   */
  async deleteEvents() {
    return await this.requests.delete(routes.aboutEvents);
  }

  /** Delete event from the Database
   */
  async deleteEvent(id: number) {
    return await this.requests.delete(routes.aboutEventsId(id));
  }
  /** Get all event_notification from the Database
   */
}
