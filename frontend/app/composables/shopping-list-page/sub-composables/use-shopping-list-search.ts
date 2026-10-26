import type { ShoppingListItemOut } from "~/lib/api/types/household";
import type { ISearchableItem } from "~/composables/use-search";
import { useSearch } from "~/composables/use-search";

/**
 * A list this size or smaller fits on a screen or two, where scrolling finds an
 * item as quickly as searching would, so the search toggle is not offered.
 */
export const SEARCH_MIN_LIST_SIZE = 20;

/**
 * Composable for searching the items on a shopping list.
 *
 * Matching is delegated to `useSearch`, so the shopping list tolerates typos and
 * ranks matches the same way every other search box in Mealie does. Only the
 * *set* of matches is used and not its order: the list stays grouped by label in
 * the user's aisle order, and non-matching items are hidden where they sit.
 *
 * This exposes a predicate rather than a filtered array because list items are
 * rendered with `v-model` bound into their backing array, and `ShoppingListItem`
 * replaces the whole item object when it is checked off. Rendering a filtered
 * copy would write that update into a throwaway array and lose it.
 */
export function useShoppingListSearch(
  listItems: Ref<ShoppingListItemOut[]> | ComputedRef<ShoppingListItemOut[]>,
) {
  /**
   * Adapt list items to `ISearchableItem`. An item is backed either by a food or
   * by a free-text note, so both have to be searchable. Unit and label are
   * matched on too -- searching a label is the quickest way to narrow a long
   * list to a single aisle.
   */
  const searchableItems = computed<ISearchableItem[]>(() =>
    listItems.value.map(item => ({
      id: item.id,
      name: item.food?.name ?? item.note ?? "",
      pluralName: item.food?.pluralName ?? null,
      abbreviation: item.unit?.abbreviation ?? null,
      aliases: [
        ...(item.food?.aliases ?? []),
        // A food-backed item can still carry a note ("ripe ones"), which the
        // name above does not cover.
        ...(item.food && item.note ? [{ name: item.note }] : []),
        ...(item.unit?.name ? [{ name: item.unit.name }] : []),
        ...(item.label?.name ? [{ name: item.label.name }] : []),
      ],
    })),
  );

  // `useSearch` ranks results and falls back to a fuzzy tier for typos, which is
  // right for a dropdown where the best match sorts to the top and stray matches
  // sit harmlessly at the bottom. This list is grouped by label and keeps the
  // user's aisle order instead, so there is no "bottom" for a weak match to fall
  // to: a fuzzy hit appears under its own aisle, indistinguishable from a real
  // one. Measured against a 130-item list, the fuzzy tier turned "cash" into 11
  // matches (every "wash"/"washes"/"stash") and "milk" into 2 (camomile, family)
  // while finding nothing the deterministic tiers missed. A zero threshold keeps
  // Fuse from contributing those without touching the exact/prefix/word-prefix/
  // substring tiers, which do all the useful work here.
  const { search, debouncedSearch, filtered, reset: clearSearch } = useSearch(
    searchableItems,
    { fuseOptions: { threshold: 0 } },
  );

  const isSearching = computed(() => debouncedSearch.value.trim().length > 0);

  // The search field sits behind a toggle so it takes no room until it is
  // wanted, and is only offered once the list is long enough to need it.
  const isSearchOpen = ref(false);
  const canSearch = computed(() => listItems.value.length > SEARCH_MIN_LIST_SIZE);

  // Closing the field also clears it, so a query nobody can see never leaves
  // items hidden.
  function toggleSearch() {
    isSearchOpen.value = !isSearchOpen.value;
    if (!isSearchOpen.value) {
      clearSearch();
    }
  }

  // `filtered` returns every item while the query is empty, so this holds the
  // full set in that case and every item matches.
  const matchedIds = computed(() => new Set(filtered.value.map(item => item.id)));

  function matchesSearch(item: ShoppingListItemOut): boolean {
    return !isSearching.value || matchedIds.value.has(item.id);
  }

  function countMatches(items: ShoppingListItemOut[]): number {
    return isSearching.value ? items.filter(matchesSearch).length : items.length;
  }

  function hasMatches(items: ShoppingListItemOut[]): boolean {
    return isSearching.value ? items.some(matchesSearch) : items.length > 0;
  }

  return {
    search,
    // Exposed for the same reason `useSearch` exposes it: it is what `filtered`
    // actually reads, so tests can drive matching synchronously.
    debouncedSearch,
    isSearching,
    isSearchOpen,
    canSearch,
    toggleSearch,
    matchesSearch,
    countMatches,
    hasMatches,
    clearSearch,
  };
}
