import Admin from "@/pages/Admin";
import Migration from "@/pages/Admin/Migration";
import Profile from "@/pages/Admin/Profile";
import ManageUsers from "@/pages/Admin/ManageUsers";
import Settings from "@/pages/Admin/Settings";
import About from "@/pages/Admin/About";
import ToolBox from "@/pages/Admin/ToolBox";
import Dashboard from "@/pages/Admin/Dashboard";
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
        title: "user.manage-users",
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
      component: ToolBox,
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
    {
      path: "dashboard",
      component: Dashboard,
      meta: {
        title: "general.dashboard",
      },
    },
  ],
};
