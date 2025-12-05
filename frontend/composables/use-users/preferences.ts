import { useLocalStorage, useSessionStorage } from "@vueuse/core";
import { ActivityKey } from "~/lib/api/types/activity";
import type { RegisteredParser, TimelineEventType } from "~/lib/api/types/recipe";
import type { QueryFilterJSON } from "~/lib/api/types/response";

export interface UserPrintPreferences {
  imagePosition: string;
  showDescription: boolean;
  showNotes: boolean;
  showNutrition: boolean;
  expandChildRecipes: boolean;
}

export interface UserSearchQuery {
  recipe: string;
}

export enum ImagePosition {
  hidden = "hidden",
  left = "left",
  right = "right",
}

export interface UserMealPlanPreferences {
  numberOfDays: number;
}

export interface UserRecipePreferences {
  orderBy: string;
  orderDirection: string;
  filterNull: boolean;
  sortIcon: string;
  useMobileCards: boolean;
}

export interface UserShoppingListPreferences {
  viewAllLists: boolean;
}

export interface UserTimelinePreferences {
  orderDirection: string;
  types: TimelineEventType[];
}

export interface UserParsingPreferences {
  parser: RegisteredParser;
}

export interface UserCookbooksPreferences {
  hideOtherHouseholds: boolean;
}

export interface UserRecipeFinderPreferences {
  foodIds: string[];
  toolIds: string[];
  queryFilter: string;
  queryFilterJSON: QueryFilterJSON;
  maxMissingFoods: number;
  maxMissingTools: number;
  includeFoodsOnHand: boolean;
  includeToolsOnHand: boolean;
}

export interface UserRecipeCreatePreferences {
  importKeywordsAsTags: boolean;
  stayInEditMode: boolean;
  parseRecipe: boolean;
}

export interface UserActivityPreferences {
  defaultActivity: ActivityKey;
}

export function useUserMealPlanPreferences(): Ref<UserMealPlanPreferences> {
  const fromStorage = useLocalStorage(
    "meal-planner-preferences",
    {
      numberOfDays: 7,
    },
    { mergeDefaults: true },
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserMealPlanPreferences>;

  return fromStorage;
}

export function useUserPrintPreferences(): Ref<UserPrintPreferences> {
  const fromStorage = useLocalStorage(
    "recipe-print-preferences",
    {
      imagePosition: "left",
      showDescription: true,
      showNotes: true,
      expandChildRecipes: false,
    },
    { mergeDefaults: true },
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserPrintPreferences>;

  return fromStorage;
}

export function useUserSortPreferences(): Ref<UserRecipePreferences> {
  const { $globals } = useNuxtApp();

  const fromStorage = useLocalStorage(
    "recipe-section-preferences",
    {
      orderBy: "created_at",
      orderDirection: "desc",
      filterNull: false,
      sortIcon: $globals.icons.sortAlphabeticalAscending,
      useMobileCards: false,
    },
    { mergeDefaults: true },
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserRecipePreferences>;

  return fromStorage;
}

export function useUserActivityPreferences(): Ref<UserActivityPreferences> {
  const fromStorage = useLocalStorage(
    "activity-preferences",
    {
      defaultActivity: ActivityKey.RECIPES,
    },
    { mergeDefaults: true },
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as Ref<UserActivityPreferences>;

  return fromStorage;
}

export function useUserSearchQuerySession(): Ref<UserSearchQuery> {
  const fromStorage = useSessionStorage(
    "search-query",
    {
      recipe: "",
    },
    { mergeDefaults: true },
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserSearchQuery>;

  return fromStorage;
}

export function useShoppingListPreferences(): Ref<UserShoppingListPreferences> {
  const fromStorage = useLocalStorage(
    "shopping-list-preferences",
    {
      viewAllLists: false,
    },
    { mergeDefaults: true },
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserShoppingListPreferences>;

  return fromStorage;
}

export function useTimelinePreferences(): Ref<UserTimelinePreferences> {
  const fromStorage = useLocalStorage(
    "timeline-preferences",
    {
      orderDirection: "asc",
      types: ["info", "system", "comment"] as TimelineEventType[],
    },
    { mergeDefaults: true },
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserTimelinePreferences>;

  return fromStorage;
}

export function useParsingPreferences(): Ref<UserParsingPreferences> {
  const fromStorage = useLocalStorage(
    "parsing-preferences",
    {
      parser: "nlp",
    },
    { mergeDefaults: true },
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserParsingPreferences>;

  return fromStorage;
}

export function useCookbookPreferences(): Ref<UserCookbooksPreferences> {
  const fromStorage = useLocalStorage(
    "cookbook-preferences",
    {
      hideOtherHouseholds: false,
    },
    { mergeDefaults: true },
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserCookbooksPreferences>;

  return fromStorage;
}

export function useRecipeFinderPreferences(): Ref<UserRecipeFinderPreferences> {
  const fromStorage = useLocalStorage(
    "recipe-finder-preferences",
    {
      foodIds: [],
      toolIds: [],
      queryFilter: "",
      queryFilterJSON: { parts: [] } as QueryFilterJSON,
      maxMissingFoods: 20,
      maxMissingTools: 20,
      includeFoodsOnHand: true,
      includeToolsOnHand: true,
    },
    { mergeDefaults: true },
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserRecipeFinderPreferences>;

  return fromStorage;
}

export function useRecipeCreatePreferences(): Ref<UserRecipeCreatePreferences> {
  const fromStorage = useLocalStorage(
    "recipe-create-preferences",
    {
      importKeywordsAsTags: false,
      stayInEditMode: false,
      parseRecipe: true,
    },
    { mergeDefaults: true },
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserRecipeCreatePreferences>;

  return fromStorage;
}
