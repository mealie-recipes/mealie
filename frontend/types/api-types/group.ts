/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface CreateWebhook {
  enabled?: boolean;
  name?: string;
  url?: string;
  time?: string;
}
export interface ReadWebhook {
  enabled?: boolean;
  name?: string;
  url?: string;
  time?: string;
  groupId: string;
  id: number;
}
export interface SaveWebhook {
  enabled?: boolean;
  name?: string;
  url?: string;
  time?: string;
  groupId: string;
}
