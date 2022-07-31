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
  );

  return fromStorage;
}
