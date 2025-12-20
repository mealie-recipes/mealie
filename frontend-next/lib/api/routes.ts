/**
 * Explore group slug route helper
 * @param groupSlug Group slug or ID
 * @returns The route for the specified group slug
 */
const exploreGroupSlug = (groupSlug: string | number) =>
  `/explore/groups/${groupSlug}`;

/**
 * API route constants for the application
 */
export const API_ROUTES = {
  AUTH: {
    TOKEN: "/api/auth/token",
    OAUTH: "/api/auth/oauth",
    OAUTH_CALLBACK: (searchParms: string) =>
      `/api/auth/oauth/callback?${searchParms}`,
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
        `/api/users/self/ratings/${recipe_id}`,
      FAVORITES: "/api/users/self/favorites",
      UPDATE_PASSWORD: "/api/users/self/password",
      UPDATE_USER: (item_id: string) => `/api/users/${item_id}`,
    },
    PASSWORDS: {
      FORGOT: "/api/users/forgot-password",
      RESET: "/api/users/reset-password",
    },
    IMAGES: {
      UPDATE: "/api/users/${id}/image",
    },
    TOKENS: {
      CREATE: "/api/users/api-tokens",
      DELETE: (token_id: string) => `/api/users/api-tokens/${token_id}`,
    },
    RATINGS: {
      GET: (id: string) => `/api/users/${id}/ratings/`,
      FAVORITES: (id: string) => `/api/users/${id}/favorites`,
      SET_RATING: (id: string, slug: string) =>
        `/api/users/${id}/ratings/${slug}`,
      ADD_FAVORITE: (id: string, slug: string) =>
        `/api/users/${id}/favorites/${slug}`,
      DELETE_FAVORITE: (id: string, slug: string) =>
        `/api/users/${id}/favorites/${slug}`,
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
      ) => `${exploreGroupSlug(groupSlug)}/cookbooks/${cookbookId}`,
      foodsGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/foods`,
      foodsGroupSlugFoodId: (
        groupSlug: string | number,
        foodId: string | number
      ) => `${exploreGroupSlug(groupSlug)}/foods/${foodId}`,
      householdsGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/households`,
      householdsGroupSlugHouseholdSlug: (
        groupSlug: string | number,
        householdSlug: string | number
      ) => `${exploreGroupSlug(groupSlug)}/households/${householdSlug}`,
      categoriesGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/organizers/categories`,
      categoriesGroupSlugCategoryId: (
        groupSlug: string | number,
        categoryId: string | number
      ) => `${exploreGroupSlug(groupSlug)}/organizers/categories/${categoryId}`,
      tagsGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/organizers/tags`,
      tagsGroupSlugTagId: (
        groupSlug: string | number,
        tagId: string | number
      ) => `${exploreGroupSlug(groupSlug)}/organizers/tags/${tagId}`,
      toolsGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/organizers/tools`,
      toolsGroupSlugToolId: (
        groupSlug: string | number,
        toolId: string | number
      ) => `${exploreGroupSlug(groupSlug)}/organizers/tools`,
      recipesGroupSlug: (groupSlug: string | number) =>
        `${exploreGroupSlug(groupSlug)}/recipes`,
      recipesGroupSlugRecipeSlug: (
        groupSlug: string | number,
        recipeSlug: string | number
      ) => `${exploreGroupSlug(groupSlug)}/recipes/${recipeSlug}`,
    },
    VALIDATORS: {
      group: (name: string) => `/api/validators/group?name=${name}`,
      user: (name: string) => `/api/validators/user/name?name=${name}`,
      email: (name: string) => `/api/validators/user/email?email=${name}`,
      recipe: (groupId: string, name: string) =>
        `/api/validators/group/recipe?group_id=${groupId}?name=${name}`,
    },
    SHARED: {
      recipeShareToken: (token: string) => `/api/recipes/shared/${token}`,
    },
  },
};
