import backup from "./api/backup";
import recipe from "./api/recipe";
import mealplan from "./api/mealplan";
import settings from "./api/settings";
import themes from "./api/themes";
import migration from "./api/migration";
import myUtils from "./api/upload";
import category from "./api/category";
import meta from "./api/meta";

// import api from "@/api";

export default {
  recipes: recipe,
  backups: backup,
  mealPlans: mealplan,
  settings: settings,
  themes: themes,
  migrations: migration,
  utils: myUtils,
  categories: category,
  meta: meta,
};
