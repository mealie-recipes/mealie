import backup from "./api/backup";
import recipe from "./api/recipe";
import mealplan from "./api/mealplan";
import settings from "./api/settings";
import themes from "./api/themes";

// import api from "../api";

export default {
  recipes: recipe,
  backups: backup,
  mealPlans: mealplan,
  settings: settings,
  themes: themes,
};
