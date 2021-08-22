import { BaseCRUDAPI } from "./_base";

export type EventCategory = "general" | "recipe" | "backup" | "scheduled" | "migration" | "group" | "user";
export type DeclaredTypes = "General" | "Discord" | "Gotify" | "Pushover" | "Home Assistant";
export type GotifyPriority = "low" | "moderate" | "normal" | "high";

export interface EventNotification {
  id?: number;
  name?: string;
  type?: DeclaredTypes & string;
  general?: boolean;
  recipe?: boolean;
  backup?: boolean;
  scheduled?: boolean;
  migration?: boolean;
  group?: boolean;
  user?: boolean;
}

export interface CreateEventNotification extends EventNotification {
  notificationUrl?: string;
}

const prefix = "/api";

const routes = {
  aboutEventsNotifications: `${prefix}/about/events/notifications`,
  aboutEventsNotificationsTest: `${prefix}/about/events/notifications/test`,

  aboutEventsNotificationsId: (id: number) => `${prefix}/about/events/notifications/${id}`,
};

export class NotificationsAPI extends BaseCRUDAPI<EventNotification, CreateEventNotification> {
  baseRoute = routes.aboutEventsNotifications;
  itemRoute = routes.aboutEventsNotificationsId;
  /** Returns the Group Data for the Current User
   */
  async testNotification(id: number | null = null, testUrl: string | null = null) {
    return await this.requests.post(routes.aboutEventsNotificationsTest, { id, testUrl });
  }
}
