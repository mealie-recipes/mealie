import { useRecipeCreatePreferences } from "~/composables/use-users/preferences";

export interface UseNewRecipeOptionsProps {
  enableImportKeywords?: boolean;
  enableImportCategories?: boolean;
  enableStayInEditMode?: boolean;
  enableParseRecipe?: boolean;
}

export function useNewRecipeOptions(props: UseNewRecipeOptionsProps = {}) {
  const {
    enableImportKeywords = true,
    enableImportCategories = true,
    enableStayInEditMode = true,
    enableParseRecipe = true,
  } = props;

  const router = useRouter();
  const recipeCreatePreferences = useRecipeCreatePreferences();

  const importKeywordsAsTags = computed({
    get() {
      if (!enableImportKeywords) return false;
      return recipeCreatePreferences.value.importKeywordsAsTags;
    },
    set(v: boolean) {
      if (!enableImportKeywords) return;
      recipeCreatePreferences.value.importKeywordsAsTags = v;
    },
  });

  const importCategories = computed({
    get() {
      if (!enableImportCategories) return false;
      return recipeCreatePreferences.value.importCategories;
    },
    set(v: boolean) {
      if (!enableImportCategories) return;
      recipeCreatePreferences.value.importCategories = v;
    },
  });

  const stayInEditMode = computed({
    get() {
      if (!enableStayInEditMode) return false;
      return recipeCreatePreferences.value.stayInEditMode;
    },
    set(v: boolean) {
      if (!enableStayInEditMode) return;
      recipeCreatePreferences.value.stayInEditMode = v;
    },
  });

  const parseRecipe = computed({
    get() {
      if (!enableParseRecipe) return false;
      return recipeCreatePreferences.value.parseRecipe;
    },
    set(v: boolean) {
      if (!enableParseRecipe) return;
      recipeCreatePreferences.value.parseRecipe = v;
    },
  });

  function navigateToRecipe(recipeSlug: string, groupSlug: string, createPagePath: string) {
    const editParam = enableStayInEditMode ? stayInEditMode.value : false;
    const parseParam = enableParseRecipe ? parseRecipe.value : false;

    const queryParams = new URLSearchParams();
    if (editParam) {
      queryParams.set("edit", "true");
    }
    if (parseParam) {
      queryParams.set("parse", "true");
    }

    const queryString = queryParams.toString();
    const recipeUrl = `/g/${groupSlug}/r/${recipeSlug}${queryString ? `?${queryString}` : ""}`;

    // Replace current entry to prevent re-import on back navigation
    router.replace(createPagePath).then(() => router.push(recipeUrl));
  }

  return {
    // Computed properties for the checkboxes
    importKeywordsAsTags,
    importCategories,
    stayInEditMode,
    parseRecipe,

    // Helper functions
    navigateToRecipe,

    // Props for conditional rendering
    enableImportKeywords,
    enableImportCategories,
    enableStayInEditMode,
    enableParseRecipe,
  };
}
