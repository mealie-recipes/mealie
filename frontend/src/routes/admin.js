import Admin from "../pages/Admin";
import General from "../components/Admin/General";
import Backup from "../components/Admin/Backup";
import Theme from "../components/Admin/Theme";
import MealPlanner from "../components/Admin/MealPlanner";
import Migration from "../components/Admin/Migration";
import Profile from "../pages/Admin/Profile";
import ManageUsers from "../pages/Admin/ManageUsers";
import Settings from "../pages/Admin/Settings";

export default {
  path: "/admin",
  component: Admin,
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
      path: "general",
      component: General,
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
  ],
};
