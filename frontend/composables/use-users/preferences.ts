import { Ref, useContext } from "@nuxtjs/composition-api";
import { useLocalStorage } from "@vueuse/core";

export interface UserRecipePreferences {
  orderBy: string;
  orderDirection: string;
  sortIcon: string;
  useMobileCards: boolean;
}

export function useUserSortPreferences(): Ref<UserRecipePreferences> {
  const { $globals } = useContext();

  const fromStorage = useLocalStorage(
    "recipe-section-preferences",
    {
      orderBy: "name",
      orderDirection: "asc",
      sortIcon: $globals.icons.sortAlphabeticalAscending,
      useMobileCards: false,
    },
    { mergeDefaults: true }
    // we cast to a Ref because by default it will return an optional type ref
    // but since we pass defaults we know all properties are set.
  ) as unknown as Ref<UserRecipePreferences>;

  return fromStorage;
}
