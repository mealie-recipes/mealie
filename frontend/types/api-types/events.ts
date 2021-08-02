/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type EventCategory = "general" | "recipe" | "backup" | "scheduled" | "migration" | "group" | "user";
export type DeclaredTypes = "General" | "Discord" | "Gotify" | "Pushover" | "Home Assistant";
export type GotifyPriority = "low" | "moderate" | "normal" | "high";

export interface Discord {
  webhookId: string;
  webhookToken: string;
}
export interface Event {
  id?: number;
  title: string;
  text: string;
  timeStamp?: string;
  category?: EventCategory & string;
}
export interface EventNotificationIn {
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
  notificationUrl?: string;
}
export interface EventNotificationOut {
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
export interface EventsOut {
  total: number;
  events: Event[];
}
export interface Gotify {
  hostname: string;
  token: string;
  priority?: GotifyPriority & string;
}
export interface TestEvent {
  id?: number;
  testUrl?: string;
}
