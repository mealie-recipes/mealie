const ViewRecipe = () => import("@/pages/Recipe/ViewRecipe");
const NewRecipe = () => import("@/pages/Recipe/NewRecipe");
const CustomPage = () => import("@/pages/Recipes/CustomPage");
const AllRecipes = () => import("@/pages/Recipes/AllRecipes");
const CategoryTagPage = () => import("@/pages/Recipes/CategoryTagPage");
import { api } from "@/api";

export const recipeRoutes = [
  // Recipes
  { path: "/recipes/all", component: AllRecipes },
  { path: "/recipes/tag/:tag", component: CategoryTagPage },
  { path: "/recipes/tag", component: CategoryTagPage },
  { path: "/recipes/category", component: CategoryTagPage },
  { path: "/recipes/category/:category", component: CategoryTagPage },
  // Misc
  { path: "/new/", component: NewRecipe },
  { path: "/pages/:customPage", component: CustomPage },

  // Recipe Page
  {
    path: "/recipe/:recipe",
    component: ViewRecipe,
    meta: {
      title: async route => {
        const recipe = await api.recipes.requestDetails(route.params.recipe);
        return recipe.name;
      },
    },
  },
];
