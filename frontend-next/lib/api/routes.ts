/**
 * Explore group slug route helper
 * @param groupSlug Group slug or ID
 * @returns The route for the specified group slug
 */
const exploreGroupSlug = (groupSlug: string | number) =>
  `/explore/groups/${encodeURIComponent(groupSlug)}`;

/**
 * API route constants for the application
 */
export const API_ROUTES = {
  AUTH: {
    TOKEN: "/api/auth/token",
    OAUTH: "/api/auth/oauth",
    OAUTH_CALLBACK: (searchParams: string) =>
      `/api/auth/oauth/callback?${searchParams}`,
    REFRESH: "/api/auth/refresh",
    LOGOUT: "/api/auth/logout",
  },
  APP: {
    CONFIG: "/api/app/about",
    STARTUP_INFO: "/api/app/about/startup-info",
    THEME: "/api/app/theme",
  },
  USERS: {
    REGISTRATION: "/api/users/register",
    CRUD: {
      SELF: "/api/users/self",
      RATINGS: "/api/users/self/ratings",
      RECIPE_RATING: (recipe_id: string) =>
        `/api/users/self/ratings/${encodeURIComponent(recipe_id)}`,
      FAVORITES: "/api/users/self/favorites",
      UPDATE_PASSWORD: "/api/users/self/password",
      UPDATE_USER: (item_id: string) =>
        `/api/users/${encodeURIComponent(item_id)}`,
    },
    PASSWORDS: {
      FORGOT: "/api/users/forgot-password",
      RESET: "/api/users/reset-password",
    },
    IMAGES: {
      UPDATE: (id: string) => `/api/users/${encodeURIComponent(id)}/image`,
    },
    TOKENS: {
      CREATE: "/api/users/api-tokens",
      DELETE: (token_id: string) =>
        `/api/users/api-tokens/${encodeURIComponent(token_id)}`,
    },
    RATINGS: {
      GET: (id: string) => `/api/users/${encodeURIComponent(id)}/ratings/`,
      FAVORITES: (id: string) =>
        `/api/users/${encodeURIComponent(id)}/favorites`,
      SET_RATING: (id: string, slug: string) =>
        `/api/users/${encodeURIComponent(id)}/ratings/${encodeURIComponent(
          slug
        )}`,
      ADD_FAVORITE: (id: string, slug: string) =>
        `/api/users/${encodeURIComponent(id)}/favorites/${encodeURIComponent(
          slug
        )}`,
      DELETE_FAVORITE: (id: string, slug: string) =>
        `/api/users/${encodeURIComponent(id)}/favorites/${encodeURIComponent(
          slug
        )}`,
    },
  },
  PUBLIC_ROUTES: {
    APP: {
      ABOUT: "/api/app/about",
      STARTUP_INFO: "/api/app/about/startup-info",
      THEME: "/api/app/theme",
    },
    EXPLORE: {
      exploreGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}`,
      cookbooksGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/cookbooks`,
      cookbooksGroupSlugCookbookId: (
        groupSlug: string | number,
        cookbookId: string | number
      ) =>
        `${exploreGroupSlug(groupSlug)}/cookbooks/${encodeURIComponent(
          cookbookId
        )}`,
      foodsGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/foods`,
      foodsGroupSlugFoodId: (
        groupSlug: string | number,
        foodId: string | number
      ) => `${exploreGroupSlug(groupSlug)}/foods/${encodeURIComponent(foodId)}`,
      householdsGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/households`,
      householdsGroupSlugHouseholdSlug: (
        groupSlug: string | number,
        householdSlug: string | number
      ) =>
        `${exploreGroupSlug(groupSlug)}/households/${encodeURIComponent(
          householdSlug
        )}`,
      categoriesGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/organizers/categories`,
      categoriesGroupSlugCategoryId: (
        groupSlug: string | number,
        categoryId: string | number
      ) =>
        `${exploreGroupSlug(
          groupSlug
        )}/organizers/categories/${encodeURIComponent(categoryId)}`,
      tagsGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/organizers/tags`,
      tagsGroupSlugTagId: (
        groupSlug: string | number,
        tagId: string | number
      ) =>
        `${exploreGroupSlug(groupSlug)}/organizers/tags/${encodeURIComponent(
          tagId
        )}`,
      toolsGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/organizers/tools`,
      toolsGroupSlugToolId: (
        groupSlug: string | number,
        toolId: string | number
      ) =>
        `/explore/groups/${encodeURIComponent(
          groupSlug
        )}/organizers/tools/${encodeURIComponent(toolId)}`,
      recipesGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/recipes`,
      recipesGroupSlugRecipeSlug: (
        groupSlug: string | number,
        recipeSlug: string | number
      ) =>
        `${exploreGroupSlug(groupSlug)}/recipes/${encodeURIComponent(
          recipeSlug
        )}`,
    },
    VALIDATORS: {
      group: (name: string) =>
        `/api/validators/group?name=${encodeURIComponent(name)}`,
      user: (name: string) =>
        `/api/validators/user/name?name=${encodeURIComponent(name)}`,
      email: (name: string) =>
        `/api/validators/user/email?email=${encodeURIComponent(name)}`,
      recipe: (groupId: string, name: string) =>
        `/api/validators/group/recipe?group_id=${encodeURIComponent(
          groupId
        )}&name=${encodeURIComponent(name)}`,
    },
    SHARED: {
      recipeShareToken: (token: string) =>
        `/api/recipes/shared/${encodeURIComponent(token)}`,
    },
  },
};
