/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type ServerTaskNames = "Background Task" | "Database Backup" | "Bulk Recipe Import";
export type ServerTaskStatus = "running" | "finished" | "failed";

export interface ServerTask {
  groupId: string;
  name?: ServerTaskNames & string;
  createdAt?: string;
  status?: ServerTaskStatus & string;
  log?: string;
  id: number;
}
export interface ServerTaskCreate {
  groupId: string;
  name?: ServerTaskNames & string;
  createdAt?: string;
  status?: ServerTaskStatus & string;
  log?: string;
}
