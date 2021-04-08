import Admin from "@/pages/Admin";
import Backup from "@/pages/Admin/Backup";
import Theme from "@/pages/Admin/Theme";
import MealPlanner from "@/pages/Admin/MealPlanner";
import Migration from "@/pages/Admin/Migration";
import Profile from "@/pages/Admin/Profile";
import ManageUsers from "@/pages/Admin/ManageUsers";
import Settings from "@/pages/Admin/Settings";
import About from "@/pages/Admin/About";
import ToolBox from "@/pages/Admin/ToolBox";
import { store } from "../store";

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
    },

    {
      path: "backups",
      component: Backup,
    },
    {
      path: "themes",
      component: Theme,
    },
    {
      path: "meal-planner",
      component: MealPlanner,
    },
    {
      path: "migrations",
      component: Migration,
    },
    {
      path: "manage-users",
      component: ManageUsers,
    },
    {
      path: "settings",
      component: Settings,
    },
    {
      path: "about",
      component: About,
    },
    {
      path: "tool-box",
      component: ToolBox,
    },
  ],
};
