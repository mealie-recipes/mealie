import Admin from "@/pages/Admin";
import General from "@/pages/Admin/General";
import Backup from "@/pages/Admin/Backup";
import Theme from "@/pages/Admin/Theme";
import MealPlanner from "@/pages/Admin/MealPlanner";
import Migration from "@/pages/Admin/Migration";
import Profile from "@/pages/Admin/Profile";
import ManageUsers from "@/pages/Admin/ManageUsers";
import Settings from "@/pages/Admin/Settings";

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
