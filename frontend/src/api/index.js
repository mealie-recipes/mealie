import { backupAPI } from "./backup";
import { recipeAPI } from "./recipe";
import { mealplanAPI } from "./mealplan";
import { settingsAPI } from "./settings";
import { themeAPI } from "./themes";
import { migrationAPI } from "./migration";
import { utilsAPI } from "./upload";
import { categoryAPI, tagAPI } from "./category";
import { metaAPI } from "./meta";
import { userAPI } from "./users";
import { signupAPI } from "./signUps";
import { groupAPI } from "./groups";
import { siteSettingsAPI } from "./siteSettings";

/**
 * The main object namespace for interacting with the backend database
 */
export const api = {
  recipes: recipeAPI,
  siteSettings: siteSettingsAPI,
  backups: backupAPI,
  mealPlans: mealplanAPI,
  settings: settingsAPI,
  themes: themeAPI,
  migrations: migrationAPI,
  utils: utilsAPI,
  categories: categoryAPI,
  tags: tagAPI,
  meta: metaAPI,
  users: userAPI,
  signUps: signupAPI,
  groups: groupAPI,
};
