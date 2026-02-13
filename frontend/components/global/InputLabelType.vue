<template>
  <v-autocomplete
    ref="autocompleteRef"
    v-model="itemVal"
    v-bind="$attrs"
    v-model:search="searchInput"
    item-title="name"
    return-object
    :items="filteredItems"
    :prepend-icon="icon || $globals.icons.tags"
    auto-select-first
    clearable
    color="primary"
    hide-details
    :custom-filter="() => true"
    @keyup.enter="emitCreate"
  >
    <template
      v-if="create"
      #append-item
    >
      <div class="px-2">
        <BaseButton
          block
          size="small"
          @click="emitCreate"
        />
      </div>
    </template>
  </v-autocomplete>
</template>

<script lang="ts">
/**
 * The InputLabelType component is a wrapper for v-autocomplete. It is used to abstract the selection functionality
 * of some common types within Mealie. This can mostly be used with any type of object provided it has a name and id
 * property. The name property is used to display the name of the object in the autocomplete dropdown. The id property
 * is used to store the id of the object in the itemId property.
 *
 * Supported Types
 *  - MultiPurposeLabel
 *  - RecipeIngredientFood
 *  - RecipeIngredientUnit
 *
 * TODO: Add RecipeTag / Category to this selector
 * Future Supported Types
 *  - RecipeTags
 *  - RecipeCategories
 *
 * Both the ID and Item can be synced. The item can be synced using the v-model syntax and the itemId can be synced
 * using the .sync syntax `item-id.sync="item.labelId"`
 */

import Fuse from "fuse.js";
import type { IFuseOptions } from "fuse.js";
import type { MultiPurposeLabelSummary } from "~/lib/api/types/labels";
import type { IngredientFood, IngredientUnit } from "~/lib/api/types/recipe";

export default defineNuxtComponent({
  props: {
    modelValue: {
      type: Object as () => MultiPurposeLabelSummary | IngredientFood | IngredientUnit,
      required: false,
      default: () => {
        return {};
      },
    },
    items: {
      type: Array as () => Array<MultiPurposeLabelSummary | IngredientFood | IngredientUnit>,
      required: true,
    },
    itemId: {
      type: [String, Number],
      default: undefined,
    },
    icon: {
      type: String,
      required: false,
      default: undefined,
    },
    create: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["update:modelValue", "update:item-id", "create"],
  setup(props, context) {
    const autocompleteRef = ref<HTMLInputElement>();
    const searchInput = ref("");

    // Flatten item aliases to include as searchable text
    const searchItems = computed(() => {
      return props.items.map((item) => {
        return {
          ...item,
          // @ts-expect-error labels don't have aliases, so this will evaluate to ""
          aliasesText: item.aliases ? item.aliases.map((a: any) => a.name).join(" ") : "",
        };
      });
    });

    // Fuse configuration for relevance-sorted autocomplete
    const fuseOptions: IFuseOptions<MultiPurposeLabelSummary | IngredientFood | IngredientUnit> = {
      keys: [{ name: "name", weight: 2 }, { name: "aliasesText", weight: 1 }],
      ignoreLocation: true,
      shouldSort: true,
      threshold: 0.3,
      minMatchCharLength: 1,
      findAllMatches: false,
    };

    const fuse = computed(() => {
      return new Fuse(searchItems.value || [], fuseOptions);
    });

    // Filter items using Fuse for relevance-based sorting
    const filteredItems = computed(() => {
      const search = searchInput.value.trim();

      // If no search query, return all items
      if (!search || search.length < 1) {
        return props.items;
      }

      const results = fuse.value.search(search);
      return results.map(result => result.item);
    });

    const itemIdVal = computed({
      get: () => {
        return props.itemId || undefined;
      },
      set: (val) => {
        context.emit("update:item-id", val);
      },
    });

    const itemVal = computed({
      get: () => {
        try {
          return Object.keys(props.modelValue).length !== 0 ? props.modelValue : null;
        }
        catch {
          return null;
        }
      },
      set: (val) => {
        itemIdVal.value = val?.id || undefined;
        context.emit("update:modelValue", val);
      },
    });

    function emitCreate() {
      if (props.items.some(item => item.name === searchInput.value)) {
        return;
      }
      context.emit("create", searchInput.value);
      autocompleteRef.value?.blur();
    }

    return {
      autocompleteRef,
      itemVal,
      itemIdVal,
      searchInput,
      filteredItems,
      emitCreate,
    };
  },
});
</script>
