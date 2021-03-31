import backup from "./backup";
import recipe from "./recipe";
import mealplan from "./mealplan";
import settings from "./settings";
import themes from "./themes";
import migration from "./migration";
import myUtils from "./upload";
import { categoryAPI, tagAPI } from "./category";
import meta from "./meta";
import users from "./users";
import signUps from "./signUps";
import groups from "./groups";
import siteSettings from "./siteSettings";

/**
 * The main object namespace for interacting with the backend database
 */
export const api = {
  recipes: recipe,
  siteSettings: siteSettings,
  backups: backup,
  mealPlans: mealplan,
  settings: settings,
  themes: themes,
  migrations: migration,
  utils: myUtils,
  categories: categoryAPI,
  tags: tagAPI,
  meta: meta,
  users: users,
  signUps: signUps,
  groups: groups,
};
