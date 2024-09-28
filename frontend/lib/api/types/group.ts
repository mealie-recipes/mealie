/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type SupportedMigrations =
  | "nextcloud"
  | "chowdown"
  | "copymethat"
  | "paprika"
  | "mealie_alpha"
  | "tandoor"
  | "plantoeat"
  | "myrecipebox"
  | "recipekeeper";

export interface CreateGroupPreferences {
  privateGroup?: boolean;
  groupId: string;
}
export interface DataMigrationCreate {
  sourceType: SupportedMigrations;
}
export interface GroupAdminUpdate {
  id: string;
  name: string;
  preferences?: UpdateGroupPreferences | null;
}
export interface UpdateGroupPreferences {
  privateGroup?: boolean;
}
export interface GroupDataExport {
  id: string;
  groupId: string;
  name: string;
  filename: string;
  path: string;
  size: string;
  expires: string;
}
export interface GroupStorage {
  usedStorageBytes: number;
  usedStorageStr: string;
  totalStorageBytes: number;
  totalStorageStr: string;
}
export interface ReadGroupPreferences {
  privateGroup?: boolean;
  groupId: string;
  id: string;
}
export interface SeederConfig {
  locale: string;
}
