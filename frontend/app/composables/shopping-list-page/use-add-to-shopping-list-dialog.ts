import type { ShoppingListSummary } from "~/lib/api/types/household";
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

  return {
    shoppingLists,
    open,
    addAllLoading,
    getShoppingLists,
    addAllToList,
  };
}
