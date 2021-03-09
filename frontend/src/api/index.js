import backup from "./backup";
import recipe from "./recipe";
import mealplan from "./mealplan";
import settings from "./settings";
import themes from "./themes";
import migration from "./migration";
import myUtils from "./upload";
import category from "./category";
import meta from "./meta";
import users from "./users";
import signUps from "./signUps";
import groups from "./groups";
import siteSettings from "./siteSettings";

export default {
  recipes: recipe,
  siteSettings: siteSettings,
  backups: backup,
  mealPlans: mealplan,
  settings: settings,
  themes: themes,
  migrations: migration,
  utils: myUtils,
  categories: category,
  meta: meta,
  users: users,
  signUps: signUps,
  groups: groups,
};
