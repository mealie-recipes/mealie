import { watchDebounced } from "@vueuse/core";
import type { IFuseOptions } from "fuse.js";
import Fuse from "fuse.js";

export interface IAlias {
  name: string;
}

export interface ISearchableItem {
  id: string;
  name: string;
  aliases?: IAlias[] | undefined;
}

interface ISearchItemInternal extends ISearchableItem {
  aliasesText?: string | undefined;
}

export interface ISearchOptions {
  debounceMs?: number;
  maxWaitMs?: number;
  minSearchLength?: number;
  fuseOptions?: Partial<IFuseOptions<ISearchItemInternal>>;
}

export function useSearch<T extends ISearchableItem>(
  items: ComputedRef<T[]> | Ref<T[]> | T[],
  options: ISearchOptions = {},
) {
  const {
    debounceMs = 0,
    maxWaitMs = 1500,
    minSearchLength = 1,
    fuseOptions: customFuseOptions = {},
  } = options;

  // State
  const search = ref("");
  const debouncedSearch = shallowRef("");

  // Flatten item aliases to include as searchable text
  const searchItems = computed(() => {
    const itemsArray = Array.isArray(items) ? items : items.value;
    return itemsArray.map((item) => {
      return {
        ...item,
        aliasesText: item.aliases ? item.aliases.map(a => a.name).join(" ") : "",
      } as ISearchItemInternal;
    });
  });

  // Default Fuse options
  const defaultFuseOptions: IFuseOptions<ISearchItemInternal> = {
    keys: [
      { name: "name", weight: 3 },
      { name: "pluralName", weight: 3 },
      { name: "abbreviation", weight: 2 },
      { name: "pluralAbbreviation", weight: 2 },
      { name: "aliasesText", weight: 1 },
    ],
    ignoreLocation: true,
    shouldSort: true,
    threshold: 0.3,
    minMatchCharLength: 1,
    findAllMatches: false,
  };

  // Merge custom options with defaults
  const fuseOptions = computed(() => ({
    ...defaultFuseOptions,
    ...customFuseOptions,
  }));

  // Debounce search input
  watchDebounced(
    () => search.value,
    (newSearch) => {
      debouncedSearch.value = newSearch;
    },
    { debounce: debounceMs, maxWait: maxWaitMs, immediate: false },
  );

  // Initialize Fuse instance
  const fuse = computed(() => {
    return new Fuse(searchItems.value || [], fuseOptions.value);
  });

  // Compute filtered results
  const filtered = computed(() => {
    const itemsArray = Array.isArray(items) ? items : items.value;
    const searchTerm = debouncedSearch.value.trim();

    // If no search query or less than minSearchLength characters, return all items
    if (!searchTerm || searchTerm.length < minSearchLength) {
      return itemsArray;
    }

    if (!itemsArray || itemsArray.length === 0) {
      return [];
    }

    const results = fuse.value.search(searchTerm);
    return results.map(result => result.item as T);
  });

  const reset = () => {
    search.value = "";
    debouncedSearch.value = "";
  };

  return {
    search,
    debouncedSearch,
    filtered,
    reset,
  };
}
