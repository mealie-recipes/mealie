import { useRecipeCreatePreferences } from "~/composables/use-users/preferences";

export interface UseNewRecipeOptionsProps {
  enableImportKeywords?: boolean;
  enableStayInEditMode?: boolean;
  enableParseRecipe?: boolean;
}

export function useNewRecipeOptions(props: UseNewRecipeOptionsProps = {}) {
  const {
    enableImportKeywords = true,
    enableStayInEditMode = true,
    enableParseRecipe = true,
  } = props;

  const route = useRoute();
  const router = useRouter();
  const recipeCreatePreferences = useRecipeCreatePreferences();

  // Import Keywords as Tags
  const importKeywordsAsTags = computed({
    get() {
      if (!enableImportKeywords) return false;
      // Check query param first, fall back to user preference if no query param exists
      if (route.query.use_keywords !== undefined) {
        return route.query.use_keywords === "1";
      }
      return recipeCreatePreferences.value.importKeywordsAsTags;
    },
    set(v: boolean) {
      if (!enableImportKeywords) return;
      router.replace({ query: { ...route.query, use_keywords: v ? "1" : "0" } });
      recipeCreatePreferences.value.importKeywordsAsTags = v;
    },
  });

  // Stay in Edit Mode
  const stayInEditMode = computed({
    get() {
      if (!enableStayInEditMode) return false;
      // Check query param first, fall back to user preference if no query param exists
      if (route.query.edit !== undefined) {
        return route.query.edit === "1";
      }
      return recipeCreatePreferences.value.stayInEditMode;
    },
    set(v: boolean) {
      if (!enableStayInEditMode) return;
      router.replace({ query: { ...route.query, edit: v ? "1" : "0" } });
      recipeCreatePreferences.value.stayInEditMode = v;
    },
  });

  // Parse Recipe Ingredients
  const parseRecipe = computed({
    get() {
      if (!enableParseRecipe) return false;
      // Check query param first, fall back to user preference if no query param exists
      if (route.query.parse !== undefined) {
        return route.query.parse === "1";
      }
      return recipeCreatePreferences.value.parseRecipe;
    },
    set(v: boolean) {
      if (!enableParseRecipe) return;
      router.replace({ query: { ...route.query, parse: v ? "1" : "0" } });
      recipeCreatePreferences.value.parseRecipe = v;
    },
  });

  // Initialize preferences from user settings and sync query params
  function initializeFromPreferences() {
    const currentQuery = { ...route.query };
    let shouldUpdateQuery = false;

    if (enableImportKeywords && route.query.use_keywords === undefined) {
      const prefValue = recipeCreatePreferences.value.importKeywordsAsTags;
      currentQuery.use_keywords = prefValue ? "1" : "0";
      shouldUpdateQuery = true;
    }

    if (enableStayInEditMode && route.query.edit === undefined) {
      const prefValue = recipeCreatePreferences.value.stayInEditMode;
      currentQuery.edit = prefValue ? "1" : "0";
      shouldUpdateQuery = true;
    }

    if (enableParseRecipe && route.query.parse === undefined) {
      const prefValue = recipeCreatePreferences.value.parseRecipe;
      currentQuery.parse = prefValue ? "1" : "0";
      shouldUpdateQuery = true;
    }

    // Update query params if any were missing
    if (shouldUpdateQuery) {
      router.replace({ query: currentQuery });
    }
  }

  // Navigate to recipe after successful creation
  function navigateToRecipe(recipeSlug: string, groupSlug: string, createPagePath: string) {
    const editParam = enableStayInEditMode ? stayInEditMode.value : false;
    const parseParam = enableParseRecipe ? parseRecipe.value : false;

    // Replace current entry without params to prevent re-import on back navigation
    router.replace(createPagePath).then(
      () => router.push(`/g/${groupSlug}/r/${recipeSlug}?edit=${editParam.toString()}&parse=${parseParam.toString()}`),
    );
  }

  return {
    // Computed properties for the checkboxes
    importKeywordsAsTags,
    stayInEditMode,
    parseRecipe,

    // Helper functions
    initializeFromPreferences,
    navigateToRecipe,

    // Props for conditional rendering
    enableImportKeywords,
    enableStayInEditMode,
    enableParseRecipe,
  };
}
