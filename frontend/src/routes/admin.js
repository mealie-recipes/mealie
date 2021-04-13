import Admin from "@/pages/Admin";
import Backup from "@/pages/Admin/Backup";
import Theme from "@/pages/Admin/Theme";
import MealPlanner from "@/pages/Admin/MealPlanner";
import Migration from "@/pages/Admin/Migration";
import Profile from "@/pages/Admin/Profile";
import ManageUsers from "@/pages/Admin/ManageUsers";
import Settings from "@/pages/Admin/Settings";
import About from "@/pages/Admin/About";
import { store } from "../store";
import i18n from '@/i18n.js';

export default {
  path: "/admin",
  component: Admin,
  beforeEnter: (to, _from, next) => {
    if (store.getters.getIsLoggedIn) {
      next();
    } else next({ path: "/login", query: { redirect: to.fullPath } });
  },
  children: [
    {
      path: "",
      component: Profile,
    },
    {
      path: "profile",
      component: Profile,
      meta: {
        title: i18n.t('settings.profile'),
      },
    },

    {
      path: "backups",
      component: Backup,
      meta: {
        title: i18n.t('settings.backup-and-exports'),
      },
    },
    {
      path: "themes",
      component: Theme,
      meta: {
        title: i18n.t('general.themes'),
      },
    },
    {
      path: "meal-planner",
      component: MealPlanner,
      meta: {
        title: i18n.t('meal-plan.meal-planner'),
      },
    },
    {
      path: "migrations",
      component: Migration,
      meta: {
        title: i18n.t('settings.migrations'),
      },
    },
    {
      path: "manage-users",
      component: ManageUsers,
      meta: {
        title: i18n.t('settings.manage-users'),
      },
    },
    {
      path: "settings",
      component: Settings,
      meta: {
        title: i18n.t('settings.site-settings'),
      },
    },
    {
      path: "about",
      component: About,
      meta: {
        title: i18n.t('general.about'),
      },
    },
  ],
};
