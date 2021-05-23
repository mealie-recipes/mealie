import ViewRecipe from "@/pages/Recipe/ViewRecipe";
import NewRecipe from "@/pages/Recipe/NewRecipe";
import CustomPage from "@/pages/Recipes/CustomPage";
import AllRecipes from "@/pages/Recipes/AllRecipes";
import CategoryTagPage from "@/pages/Recipes/CategoryTagPage";
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
