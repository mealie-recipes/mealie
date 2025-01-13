/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface AdminAboutInfo {
  production: boolean;
  version: string;
  demoStatus: boolean;
  allowSignup: boolean;
  defaultGroupSlug?: string | null;
  defaultHouseholdSlug?: string | null;
  enableOidc: boolean;
  oidcRedirect: boolean;
  oidcProviderName: string;
  enableOpenai: boolean;
  enableOpenaiImageServices: boolean;
  versionLatest: string;
  apiPort: number;
  apiDocs: boolean;
  dbType: string;
  dbUrl?: string | null;
  defaultGroup: string;
  defaultHousehold: string;
  buildId: string;
  recipeScraperVersion: string;
}
export interface AllBackups {
  imports: BackupFile[];
  templates: string[];
}
export interface BackupFile {
  name: string;
  date: string;
  size: string;
}
export interface AppInfo {
  production: boolean;
  version: string;
  demoStatus: boolean;
  allowSignup: boolean;
  defaultGroupSlug?: string | null;
  defaultHouseholdSlug?: string | null;
  enableOidc: boolean;
  oidcRedirect: boolean;
  oidcProviderName: string;
  enableOpenai: boolean;
  enableOpenaiImageServices: boolean;
}
export interface AppStartupInfo {
  isFirstLogin: boolean;
  isDemo: boolean;
}
export interface AppStatistics {
  totalRecipes: number;
  totalUsers: number;
  totalHouseholds: number;
  totalGroups: number;
  uncategorizedRecipes: number;
  untaggedRecipes: number;
}
export interface AppTheme {
  lightPrimary?: string;
  lightAccent?: string;
  lightSecondary?: string;
  lightSuccess?: string;
  lightInfo?: string;
  lightWarning?: string;
  lightError?: string;
  darkPrimary?: string;
  darkAccent?: string;
  darkSecondary?: string;
  darkSuccess?: string;
  darkInfo?: string;
  darkWarning?: string;
  darkError?: string;
}
export interface BackupOptions {
  recipes?: boolean;
  settings?: boolean;
  themes?: boolean;
  groups?: boolean;
  users?: boolean;
  notifications?: boolean;
}
export interface CheckAppConfig {
  emailReady: boolean;
  ldapReady: boolean;
  oidcReady: boolean;
  enableOpenai: boolean;
  baseUrlSet: boolean;
  isUpToDate: boolean;
}
export interface ChowdownURL {
  url: string;
}
export interface CommentImport {
  name: string;
  status: boolean;
  exception?: string | null;
}
export interface CreateBackup {
  tag?: string | null;
  options: BackupOptions;
  templates?: string[] | null;
}
export interface CustomPageBase {
  name: string;
  slug: string | null;
  position: number;
  categories?: RecipeCategoryResponse[];
}
export interface RecipeCategoryResponse {
  name: string;
  id: string;
  slug: string;
  recipes?: RecipeSummary[];
}
export interface RecipeSummary {
  id?: string | null;
  userId?: string;
  householdId?: string;
  groupId?: string;
  name?: string | null;
  slug?: string;
  image?: unknown;
  recipeServings?: number;
  recipeYieldQuantity?: number;
  recipeYield?: string | null;
  totalTime?: string | null;
  prepTime?: string | null;
  cookTime?: string | null;
  performTime?: string | null;
  description?: string | null;
  recipeCategory?: RecipeCategory[] | null;
  tags?: RecipeTag[] | null;
  tools?: RecipeTool[];
  rating?: number | null;
  orgURL?: string | null;
  dateAdded?: string | null;
  dateUpdated?: string | null;
  createdAt?: string | null;
  updatedAt?: string | null;
  lastMade?: string | null;
}
export interface RecipeCategory {
  id?: string | null;
  name: string;
  slug: string;
  [k: string]: unknown;
}
export interface RecipeTag {
  id?: string | null;
  name: string;
  slug: string;
  [k: string]: unknown;
}
export interface RecipeTool {
  id: string;
  name: string;
  slug: string;
  householdsWithTool?: string[];
  [k: string]: unknown;
}
export interface CustomPageImport {
  name: string;
  status: boolean;
  exception?: string | null;
}
export interface CustomPageOut {
  name: string;
  slug: string | null;
  position: number;
  categories?: RecipeCategoryResponse[];
  id: number;
}
export interface DebugResponse {
  success: boolean;
  response?: string | null;
}
export interface EmailReady {
  ready: boolean;
}
export interface EmailSuccess {
  success: boolean;
  error?: string | null;
}
export interface EmailTest {
  email: string;
}
export interface GroupImport {
  name: string;
  status: boolean;
  exception?: string | null;
}
export interface ImportBase {
  name: string;
  status: boolean;
  exception?: string | null;
}
export interface ImportJob {
  recipes?: boolean;
  settings?: boolean;
  themes?: boolean;
  groups?: boolean;
  users?: boolean;
  notifications?: boolean;
  name: string;
  force?: boolean;
  rebase?: boolean;
}
export interface MaintenanceLogs {
  logs: string[];
}
export interface MaintenanceStorageDetails {
  tempDirSize: string;
  backupsDirSize: string;
  groupsDirSize: string;
  recipesDirSize: string;
  userDirSize: string;
}
export interface MaintenanceSummary {
  dataDirSize: string;
  cleanableImages: number;
  cleanableDirs: number;
}
export interface MigrationFile {
  name: string;
  date: string;
}
export interface MigrationImport {
  name: string;
  status: boolean;
  exception?: string | null;
  slug?: string | null;
}
export interface Migrations {
  type: string;
  files?: MigrationFile[];
}
export interface NotificationImport {
  name: string;
  status: boolean;
  exception?: string | null;
}
export interface RecipeImport {
  name: string;
  status: boolean;
  exception?: string | null;
  slug?: string | null;
}
export interface SettingsImport {
  name: string;
  status: boolean;
  exception?: string | null;
}
export interface UserImport {
  name: string;
  status: boolean;
  exception?: string | null;
}
