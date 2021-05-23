import SearchPage from "@/pages/SearchPage";
import HomePage from "@/pages/HomePage";
import ShoppingList from "@/pages/ShoppingList";

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
