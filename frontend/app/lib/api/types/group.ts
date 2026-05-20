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
  | "recipekeeper"
  | "cookn";

export interface AIProviderCreate {
  name: string;
  baseUrl?: string | null;
  model: string;
  timeout?: number;
  requestHeaders?: {
    [k: string]: string;
  };
  requestParams?: {
    [k: string]: string;
  };
}
export interface AIProviderOut {
  name: string;
  baseUrl?: string | null;
  model: string;
  timeout?: number;
  requestHeaders?: {
    [k: string]: string;
  };
  requestParams?: {
    [k: string]: string;
  };
  id: string;
}
export interface AIProviderSave {
  name: string;
  baseUrl?: string | null;
  model: string;
  timeout?: number;
  requestHeaders?: {
    [k: string]: string;
  };
  requestParams?: {
    [k: string]: string;
  };
  settingsId: string;
}
export interface AIProviderSettingsCreate {
  groupId: string;
}
export interface AIProviderSettingsOut {
  defaultProviderId: string | null;
  audioProviderId: string | null;
  imageProviderId: string | null;
  providers: AIProviderSummary[];
  aiEnabled: boolean;
  audioProviderEnabled: boolean;
  imageProviderEnabled: boolean;
}
export interface AIProviderSummary {
  id: string;
  name: string;
}
export interface AIProviderSettingsUpdate {
  defaultProviderId: string | null;
  audioProviderId: string | null;
  imageProviderId: string | null;
}
export interface AIProviderUpdate {
  name: string;
  baseUrl?: string | null;
  model: string;
  timeout?: number;
  requestHeaders?: {
    [k: string]: string;
  };
  requestParams?: {
    [k: string]: string;
  };
}
export interface CreateGroupPreferences {
  privateGroup?: boolean;
  showAnnouncements?: boolean;
  groupId: string;
}
export interface DataMigrationCreate {
  sourceType: SupportedMigrations;
}
export interface GroupAdminUpdate {
  id: string;
  name: string;
  preferences?: UpdateGroupPreferences | null;
  aiProviderSettings?: AIProviderSettingsUpdate | null;
}
export interface UpdateGroupPreferences {
  privateGroup?: boolean;
  showAnnouncements?: boolean;
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
  showAnnouncements?: boolean;
  groupId: string;
  id: string;
}
export interface SeederConfig {
  locale: string;
}
