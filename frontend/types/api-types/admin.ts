/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

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
export interface BackupJob {
  tag?: string;
  options: BackupOptions;
  templates?: string[];
}
export interface BackupOptions {
  recipes?: boolean;
  settings?: boolean;
  pages?: boolean;
  themes?: boolean;
  groups?: boolean;
  users?: boolean;
  notifications?: boolean;
}
export interface CategoryBase {
  name: string;
  id: number;
  slug: string;
}
export interface ChowdownURL {
  url: string;
}
export interface Colors {
  primary?: string;
  accent?: string;
  secondary?: string;
  success?: string;
  info?: string;
  warning?: string;
  error?: string;
}
export interface CustomPageBase {
  name: string;
  slug?: string;
  position: number;
  categories?: RecipeCategoryResponse[];
}
export interface RecipeCategoryResponse {
  name: string;
  id: number;
  slug: string;
  recipes?: Recipe[];
}
export interface Recipe {
  id?: number;
  name?: string;
  slug?: string;
  image?: unknown;
  description?: string;
  recipeCategory?: string[];
  tags?: string[];
  rating?: number;
  dateAdded?: string;
  dateUpdated?: string;
  recipeYield?: string;
  recipeIngredient?: RecipeIngredient[];
  recipeInstructions?: RecipeStep[];
  nutrition?: Nutrition;
  tools?: string[];
  totalTime?: string;
  prepTime?: string;
  performTime?: string;
  settings?: RecipeSettings;
  assets?: RecipeAsset[];
  notes?: RecipeNote[];
  orgURL?: string;
  extras?: {
    [k: string]: unknown;
  };
  comments?: CommentOut[];
}
export interface RecipeIngredient {
  title?: string;
  note?: string;
  unit?: RecipeIngredientUnit;
  food?: RecipeIngredientFood;
  disableAmount?: boolean;
  quantity?: number;
}
export interface RecipeIngredientUnit {
  name?: string;
  description?: string;
}
export interface RecipeIngredientFood {
  name?: string;
  description?: string;
}
export interface RecipeStep {
  title?: string;
  text: string;
}
export interface Nutrition {
  calories?: string;
  fatContent?: string;
  proteinContent?: string;
  carbohydrateContent?: string;
  fiberContent?: string;
  sodiumContent?: string;
  sugarContent?: string;
}
export interface RecipeSettings {
  public?: boolean;
  showNutrition?: boolean;
  showAssets?: boolean;
  landscapeView?: boolean;
  disableComments?: boolean;
  disableAmount?: boolean;
}
export interface RecipeAsset {
  name: string;
  icon: string;
  fileName?: string;
}
export interface RecipeNote {
  title: string;
  text: string;
}
export interface CommentOut {
  text: string;
  id: number;
  uuid: string;
  recipeSlug: string;
  dateAdded: string;
  user: UserBase;
}
export interface UserBase {
  id: number;
  username?: string;
  admin: boolean;
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
export interface DebugInfo {
  production: boolean;
  version: string;
  demoStatus: boolean;
  apiPort: number;
  apiDocs: boolean;
  dbType: string;
  dbUrl: string;
  defaultGroup: string;
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
  pages?: boolean;
  themes?: boolean;
  groups?: boolean;
  users?: boolean;
  notifications?: boolean;
  name: string;
  force?: boolean;
  rebase?: boolean;
}
export interface Imports {
  imports: LocalBackup[];
  templates: string[];
}
export interface LocalBackup {
  name: string;
  date: string;
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
export interface SiteSettings {
  language?: string;
  firstDayOfWeek?: number;
  showRecent?: boolean;
  cardsPerSection?: number;
  categories?: CategoryBase[];
}
export interface SiteTheme {
  id?: number;
  name?: string;
  colors?: Colors;
}
export interface ThemeImport {
  name: string;
  status: boolean;
  exception?: string;
}
export interface UserImport {
  name: string;
  status: boolean;
  exception?: string;
}
