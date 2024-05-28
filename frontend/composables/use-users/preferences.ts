import { Ref, useContext } from "@nuxtjs/composition-api";
import { useLocalStorage, useSessionStorage } from "@vueuse/core";
import { RegisteredParser, TimelineEventType } from "~/lib/api/types/recipe";

export interface UserPrintPreferences {
  imagePosition: string;
  showDescription: boolean;
  showNotes: boolean;
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
  viewByLabel: boolean;
}

export interface UserTimelinePreferences {
  orderDirection: string;
  types: TimelineEventType[];
}

export interface UserParsingPreferences {
  parser: RegisteredParser;
}

export function useUserMealPlanPreferences(): Ref<UserMealPlanPreferences> {
  const fromStorage = useLocalStorage(
    "meal-planner-preferences",
    {
      numberOfDays: 7,
    },
    { mergeDefaults: true }
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
    },
    { mergeDefaults: true }
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserPrintPreferences>;

  return fromStorage;
}

export function useUserSortPreferences(): Ref<UserRecipePreferences> {
  const { $globals } = useContext();

  const fromStorage = useLocalStorage(
    "recipe-section-preferences",
    {
      orderBy: "name",
      orderDirection: "asc",
      filterNull: false,
      sortIcon: $globals.icons.sortAlphabeticalAscending,
      useMobileCards: false,
    },
    { mergeDefaults: true }
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserRecipePreferences>;

  return fromStorage;
}

export function useUserSearchQuerySession(): Ref<UserSearchQuery> {
  const fromStorage = useSessionStorage(
    "search-query",
    {
      recipe: "",
    },
    { mergeDefaults: true }
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
      viewByLabel: false,
    },
    { mergeDefaults: true }
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
    { mergeDefaults: true }
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
    { mergeDefaults: true }
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserParsingPreferences>;

  return fromStorage;
}
