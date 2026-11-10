import type { ShoppingListSummary } from "~/lib/api/types/household";
import { alert } from "~/composables/use-toast";
import { useUserApi } from "../api";

export function useAddToShoppingListDialog() {
  const api = useUserApi();
  const shoppingLists = ref<ShoppingListSummary[]>();
  const open = ref(false);
  const addAllLoading = ref(false);

  async function getShoppingLists() {
    const { data } = await api.shopping.lists.getAll(1, -1, { orderBy: "name", orderDirection: "asc" });
    if (data) {
      shoppingLists.value = data.items as ShoppingListSummary[] ?? [];
    }
  }

  async function addAllToList() {
    addAllLoading.value = true;
    await getShoppingLists();
    open.value = true;
    addAllLoading.value = false;
  }

  /** Adds a list that was created while the dialog was open, so it's still there when the dialog is reopened. */
  function addShoppingList(list: ShoppingListSummary) {
    const lists = shoppingLists.value ?? [];
    if (!lists.some(({ id }) => id === list.id)) {
      shoppingLists.value = [...lists, list];
    }
  }

  return {
    shoppingLists,
    open,
    addAllLoading,
    getShoppingLists,
    addAllToList,
    addShoppingList,
  };
}

/** State and API call behind the "new list" form of the add-to-shopping-list dialog. */
export function useNewShoppingListForm() {
  const api = useUserApi();
  const i18n = useI18n();

  const form = reactive({
    show: false,
    name: "",
    loading: false,
  });

  function reset() {
    form.show = false;
    form.name = "";
  }

  /** Creates a list from the form and closes the form. Returns `null` if no list was created. */
  async function create(): Promise<ShoppingListSummary | null> {
    const name = form.name.trim();
    if (!name || form.loading) {
      return null;
    }

    form.loading = true;
    const { data } = await api.shopping.lists.createOne({ name });
    form.loading = false;

    if (!data) {
      alert.error(i18n.t("shopping-list.failed-to-create-shopping-list"));
      return null;
    }

    reset();
    return data as ShoppingListSummary;
  }

  return {
    form,
    reset,
    create,
  };
}
