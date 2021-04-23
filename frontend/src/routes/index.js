import Page404 from "@/pages/404Page";
import { adminRoutes } from "./admin";
import { authRoutes } from "./auth";
import { recipeRoutes } from "./recipes";
import { mealRoutes } from "./meal";
import { generalRoutes } from "./general";
import { store } from "../store";
import VueRouter from "vue-router";
import VueI18n from "@/i18n";
import Vuetify from "@/plugins/vuetify";
import Vue from "vue";
import i18n from '@/i18n.js';

export const routes = [
  ...generalRoutes,
  adminRoutes,
  ...authRoutes,
  ...mealRoutes,
  ...recipeRoutes,

  { path: "*", component: Page404 },
];

const router = new VueRouter({
  routes,
  mode: process.env.NODE_ENV === "production" ? "history" : "hash",
  scrollBehavior() {
    return { x: 0, y: 0 };
  },
});

const DEFAULT_TITLE = "Mealie";
const TITLE_SEPARATOR = "🍴";
const TITLE_SUFFIX = " " + TITLE_SEPARATOR + " " + DEFAULT_TITLE;
router.afterEach(to => {
  Vue.nextTick(async () => {
    if (typeof to.meta.title === "function") {
      const title = await to.meta.title(to);
      document.title = title + TITLE_SUFFIX;
    } else {
      document.title = i18n.t(to.meta.title)
        ? i18n.t(to.meta.title) + TITLE_SUFFIX
        : DEFAULT_TITLE;
    }
  });
});

function loadLocale() {
  VueI18n.locale = store.getters.getActiveLang;
  Vuetify.framework.lang.current = store.getters.getActiveLang;
}

router.beforeEach((__, _, next) => {
  loadLocale();
  next();
});

export { router };
