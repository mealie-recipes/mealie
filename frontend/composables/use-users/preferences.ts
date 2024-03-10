import { Ref, useContext } from "@nuxtjs/composition-api";
import { useLocalStorage } from "@vueuse/core";

export interface UserPrintPreferences {
  imagePosition: string;
  showDescription: boolean;
  showNotes: boolean;
}

export enum ImagePosition {
  hidden = "hidden",
  left = "left",
  right = "right",
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
    },
    { mergeDefaults: true }
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserTimelinePreferences>;

  return fromStorage;
}
