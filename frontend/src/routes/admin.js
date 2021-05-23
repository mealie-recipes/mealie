const Admin = () => import("@/pages/Admin");
const Migration = () => import("@/pages/Admin/Migration");
const Profile = () => import("@/pages/Admin/Profile");
const ManageUsers = () => import("@/pages/Admin/ManageUsers");
const Settings = () => import("@/pages/Admin/Settings");
const About = () => import("@/pages/Admin/About");
const ToolBox = () => import("@/pages/Admin/ToolBox");
const Dashboard = () => import("@/pages/Admin/Dashboard");
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
