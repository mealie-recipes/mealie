import type { Ref, WritableComputedRef } from "vue";
import type { ShoppingListItemOut } from "~/lib/api/types/household";

export interface ShopModeSection {
  label: string;
  items: ShoppingListItemOut[];
}

interface UseShoppingListShopModeOptions {
  shopQuery: WritableComputedRef<string | null | undefined>;
  itemsByLabel: Ref<{ [key: string]: ShoppingListItemOut[] }>;
}

/**
 * State of the shopping mode. The URL is the only source of truth for whether the mode is on,
 * so it survives a reload the way `?cook=true` does. The completed switch is deliberately not
 * persisted: it starts off every time the mode is entered.
 */
export function useShoppingListShopMode({ shopQuery, itemsByLabel }: UseShoppingListShopModeOptions) {
  const isShopMode = computed(() => shopQuery.value === "true");
  const showChecked = ref(false);

  watch(isShopMode, () => {
    showChecked.value = false;
  });

  function enterShopMode() {
    shopQuery.value = "true";
  }

  function exitShopMode() {
    shopQuery.value = undefined;
  }

  // itemsByLabel holds only unchecked items, in list order
  const sections = computed<ShopModeSection[]>(() =>
    Object.entries(itemsByLabel.value)
      .filter(([, items]) => items.length > 0)
      .map(([label, items]) => ({ label, items })),
  );

  const remainingCount = computed(() => sections.value.reduce((sum, section) => sum + section.items.length, 0));

  return {
    isShopMode,
    showChecked,
    sections,
    remainingCount,
    enterShopMode,
    exitShopMode,
  };
}
