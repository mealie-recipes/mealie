import Admin from "@/pages/Admin";
import Backup from "@/pages/Admin/Backup";
import Theme from "@/pages/Admin/Theme";
import MealPlanner from "@/pages/Admin/MealPlanner";
import Migration from "@/pages/Admin/Migration";
import Profile from "@/pages/Admin/Profile";
import ManageUsers from "@/pages/Admin/ManageUsers";
import Settings from "@/pages/Admin/Settings";
import About from "@/pages/Admin/About";
import Toolbox from "@/pages/Admin/Toolbox";
import { store } from "../store";

export const adminRoutes = {
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
        title: "settings.profile",
      },
    },

    {
      path: "backups",
      component: Backup,
      meta: {
        title: "settings.backup-and-exports",
      },
    },
    {
      path: "themes",
      component: Theme,
      meta: {
        title: "general.themes",
      },
    },
    {
      path: "meal-planner",
      component: MealPlanner,
      meta: {
        title: "meal-plan.meal-planner",
      },
    },
    {
      path: "migrations",
      component: Migration,
      meta: {
        title: "settings.migrations",
      },
    },
    {
      path: "manage-users",
      component: ManageUsers,
      meta: {
        title: "settings.manage-users",
      },
    },
    {
      path: "settings",
      component: Settings,
      meta: {
        title: "settings.site-settings",
      },
    },
    {
      path: "toolbox",
      component: Toolbox,
      meta: {
        title: "settings.toolbox.toolbox",
      },
    },
    {
      path: "about",
      component: About,
      meta: {
        title: "general.about",
      },
    },
  ],
};
