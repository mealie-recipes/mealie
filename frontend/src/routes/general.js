import SearchPage from "@/pages/SearchPage";
import HomePage from "@/pages/HomePage";

export const generalRoutes = [
  { path: "/", name: "home", component: HomePage },
  { path: "/mealie", component: HomePage },
  {
    path: "/search",
    component: SearchPage,
    meta: {
      title: "search.search",
    },
  },
];
