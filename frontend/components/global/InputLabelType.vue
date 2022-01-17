<template>
  <v-autocomplete
    v-model="itemVal"
    v-bind="$attrs"
    item-text="name"
    return-object
    :items="items"
    :prepend-icon="icon || $globals.icons.tags"
    clearable
    hide-details
  />
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
import { defineComponent, computed } from "@nuxtjs/composition-api";
import { MultiPurposeLabelSummary } from "~/types/api-types/labels";
import { IngredientFood, IngredientUnit } from "~/types/api-types/recipe";

export default defineComponent({
  props: {
    value: {
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
  },
  setup(props, context) {
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
        return props.value;
      },
      set: (val) => {
        itemIdVal.value = val?.id || undefined;
        context.emit("input", val);
      },
    });

    return {
      itemVal,
      itemIdVal,
    };
  },
});
</script>