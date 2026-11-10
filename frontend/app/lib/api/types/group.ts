/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type AIPromptMode = "append" | "override";
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

export interface AIPromptOut {
  name: string;
  isSystem: boolean;
  defaultContent: string;
  mode: AIPromptMode | null;
  content: string | null;
  defaultChanged: boolean;
}
export interface AIPromptOverrideCreate {
  mode: AIPromptMode;
  content: string;
  name: string;
  basePromptHash?: string | null;
}
export interface AIPromptOverrideOut {
  mode: AIPromptMode;
  content: string;
  name: string;
  basePromptHash: string | null;
  id: string;
}
export interface AIPromptOverrideUpdate {
  mode: AIPromptMode;
  content: string;
}
export interface AIPromptsOut {
  globalInstructions: string | null;
  prompts: AIPromptOut[];
}
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
  baseUrl: string | null;
  model: string;
  timeout: number;
  requestHeaders: {
    [k: string]: string;
  };
  requestParams: {
    [k: string]: string;
  };
  id: string;
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
export interface AIProviderTestResult {
  success: boolean;
  message?: string | null;
  supportsImages?: boolean | null;
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
export interface DataMigrationCreate {
  sourceType: SupportedMigrations;
}
export interface GroupAdminUpdate {
  id: string;
  name: string;
  preferences?: GroupPreferencesUpdate | null;
  aiProviderSettings?: AIProviderSettingsUpdate | null;
}
export interface GroupPreferencesUpdate {
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
export interface GroupPreferencesCreate {
  privateGroup?: boolean;
  showAnnouncements?: boolean;
  groupId: string;
}
export interface GroupPreferencesOut {
  privateGroup: boolean;
  showAnnouncements: boolean;
  groupId: string;
  id: string;
}
export interface GroupStorage {
  usedStorageBytes: number;
  usedStorageStr: string;
  totalStorageBytes: number;
  totalStorageStr: string;
}
export interface SeederConfig {
  locale: string;
}
export interface MealieOutModel {}
