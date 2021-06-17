const SearchPage = () => import("@/pages/SearchPage");
const ShoppingList = () => import("@/pages/ShoppingList");
import HomePage from "@/pages/HomePage";

export const generalRoutes = [
  { path: "/", name: "home", component: HomePage },
  { path: "/mealie", component: HomePage },
  { path: "/shopping-list", component: ShoppingList },
  {
    path: "/search",
    component: SearchPage,
    meta: {
      title: "search.search",
    },
  },
];
