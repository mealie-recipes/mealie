const Admin = () => import(/* webpackChunkName: "admin" */ "@/pages/Admin");
const Migration = () => import(/* webpackChunkName: "admin" */ "@/pages/Admin/Migration");
const Profile = () => import(/* webpackChunkName: "admin" */ "@/pages/Admin/Profile");
const ManageUsers = () => import(/* webpackChunkName: "admin" */ "@/pages/Admin/ManageUsers");
const Settings = () => import(/* webpackChunkName: "admin" */ "@/pages/Admin/Settings");
const About = () => import(/* webpackChunkName: "admin" */ "@/pages/Admin/About");
const ToolBox = () => import(/* webpackChunkName: "admin" */ "@/pages/Admin/ToolBox");
const Dashboard = () => import(/* webpackChunkName: "admin" */ "@/pages/Admin/Dashboard");
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
