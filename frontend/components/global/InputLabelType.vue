<template>
  <v-autocomplete
    ref="autocompleteRef"
    v-model="itemVal"
    v-bind="$attrs"
    v-model:search="searchInput"
    item-title="name"
    return-object
    :items="items"
    :custom-filter="normalizeFilter"
    :prepend-icon="icon || $globals.icons.tags"
    auto-select-first
    clearable
    color="primary"
    hide-details
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

import type { MultiPurposeLabelSummary } from "~/lib/api/types/labels";
import type { IngredientFood, IngredientUnit } from "~/lib/api/types/recipe";
import { normalizeFilter } from "~/composables/use-utils";

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
      emitCreate,
      normalizeFilter,
    };
  },
});
</script>
