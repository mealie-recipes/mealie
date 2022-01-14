/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

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
export interface TestEvent {
  id?: number;
  testUrl?: string;
}
