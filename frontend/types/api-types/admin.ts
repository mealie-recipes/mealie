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
  versionLatest: string;
  apiPort: number;
  apiDocs: boolean;
  dbType: string;
  dbUrl: string;
  defaultGroup: string;
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
}
export interface AppStatistics {
  totalRecipes: number;
  totalUsers: number;
  totalGroups: number;
  uncategorizedRecipes: number;
  untaggedRecipes: number;
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
  emailReady?: boolean;
  ldapReady?: boolean;
  baseUrlSet?: boolean;
  isUpToDate?: boolean;
}
export interface ChowdownURL {
  url: string;
}
export interface CommentImport {
  name: string;
  status: boolean;
  exception?: string;
}
export interface CreateBackup {
  tag?: string;
  options: BackupOptions;
  templates?: string[];
}
export interface CustomPageBase {
  name: string;
  slug?: string;
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
  id?: string;
  userId?: string;
  groupId?: string;
  name?: string;
  slug?: string;
  image?: unknown;
  recipeYield?: string;
  totalTime?: string;
  prepTime?: string;
  cookTime?: string;
  performTime?: string;
  description?: string;
  recipeCategory?: RecipeCategory[];
  tags?: RecipeTag[];
  tools?: RecipeTool[];
  rating?: number;
  orgURL?: string;
  recipeIngredient?: RecipeIngredient[];
  dateAdded?: string;
  dateUpdated?: string;
}
export interface RecipeCategory {
  id?: string;
  name: string;
  slug: string;
}
export interface RecipeTag {
  id?: string;
  name: string;
  slug: string;
}
export interface RecipeTool {
  id: string;
  name: string;
  slug: string;
  onHand?: boolean;
}
export interface RecipeIngredient {
  title?: string;
  note?: string;
  unit?: IngredientUnit | CreateIngredientUnit;
  food?: IngredientFood | CreateIngredientFood;
  disableAmount?: boolean;
  quantity?: number;
  referenceId?: string;
}
export interface IngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
  id: string;
}
export interface CreateIngredientUnit {
  name: string;
  description?: string;
  fraction?: boolean;
  abbreviation?: string;
}
export interface IngredientFood {
  name: string;
  description?: string;
  labelId?: string;
  id: string;
  label?: MultiPurposeLabelSummary;
}
export interface MultiPurposeLabelSummary {
  name: string;
  color?: string;
  groupId: string;
  id: string;
}
export interface CreateIngredientFood {
  name: string;
  description?: string;
  labelId?: string;
}
export interface CustomPageImport {
  name: string;
  status: boolean;
  exception?: string;
}
export interface CustomPageOut {
  name: string;
  slug?: string;
  position: number;
  categories?: RecipeCategoryResponse[];
  id: number;
}
export interface GroupImport {
  name: string;
  status: boolean;
  exception?: string;
}
export interface ImportBase {
  name: string;
  status: boolean;
  exception?: string;
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
export interface MigrationFile {
  name: string;
  date: string;
}
export interface MigrationImport {
  name: string;
  status: boolean;
  exception?: string;
  slug?: string;
}
export interface Migrations {
  type: string;
  files?: MigrationFile[];
}
export interface NotificationImport {
  name: string;
  status: boolean;
  exception?: string;
}
export interface RecipeImport {
  name: string;
  status: boolean;
  exception?: string;
  slug?: string;
}
export interface SettingsImport {
  name: string;
  status: boolean;
  exception?: string;
}
export interface UserImport {
  name: string;
  status: boolean;
  exception?: string;
}
