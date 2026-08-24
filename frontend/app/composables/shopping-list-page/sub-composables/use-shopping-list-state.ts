import type { ShoppingListOut, ShoppingListItemOut } from "~/lib/api/types/household";

/**
 * Composable for managing shopping list state and reactive data
 */
export function useShoppingListState() {
  const shoppingList = ref<ShoppingListOut | null>(null);
  const loadingCounter = ref(1);
  const recipeReferenceLoading = ref(false);
  const preserveItemOrder = ref(false);

  // UI state
  const edit = ref(false);
  const threeDot = ref(false);
  const reorderLabelsDialog = ref(false);
  const createEditorOpen = ref(false);

  // Dialog states
  const state = reactive({
    checkAllDialog: false,
    uncheckAllDialog: false,
    deleteCheckedDialog: false,
  });

  // Hydrate listItems from shoppingList.value?.listItems
  const listItems = reactive({
    unchecked: [] as ShoppingListItemOut[],
    checked: [] as ShoppingListItemOut[],
  });

  function sortCheckedItems(a: ShoppingListItemOut, b: ShoppingListItemOut) {
    if (a.updatedAt! === b.updatedAt!) {
      return ((a.position || 0) > (b.position || 0)) ? -1 : 1;
    }
    return a.updatedAt! < b.updatedAt! ? 1 : -1;
  }

  watch(
    () => shoppingList.value?.listItems,
    (items) => {
      listItems.unchecked = (items?.filter(item => !item.checked) ?? []);
      listItems.checked = (items?.filter(item => item.checked)
        .sort(sortCheckedItems) ?? []);
    },
    { immediate: true },
  );

  const recipeMap = computed(() => new Map(
    (shoppingList.value?.recipeReferences?.map(ref => ref.recipe) ?? [])
      .map(recipe => [recipe.id || "", recipe])),
  );

  const recipeList = computed(() => Array.from(recipeMap.value.values()));

  return {
    shoppingList,
    loadingCounter,
    recipeReferenceLoading,
    preserveItemOrder,
    edit,
    threeDot,
    reorderLabelsDialog,
    createEditorOpen,
    state,
    listItems,
    recipeMap,
    recipeList,
    sortCheckedItems,
  };
}
