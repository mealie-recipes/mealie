<template>
  <v-navigation-drawer
    ref="target"
    permanent
    rounded="t-xl"
    location="bottom"
    class="pa-4 pt-2 mb-0"
    width="300"
    rail-width="85"
    :rail="!showDetails"
    elevation="4"
  >
    <ShoppingListQuickAdd
      v-model="listItem"
      v-model:details="showDetails"
      :foods="foods"
      :labels="labels"
      :units="units"
      @save="$emit('save')"
    />
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import type { ShoppingListItemOut } from "~/lib/api/types/household";
import type { MultiPurposeLabelOut } from "~/lib/api/types/labels";
import type { IngredientFood, IngredientUnit } from "~/lib/api/types/recipe";
import ShoppingListQuickAdd from "./ShoppingListQuickAdd.vue";
import { onClickOutside } from "@vueuse/core";

// modelValue as reactive v-model
const listItem = defineModel<ShoppingListItemOut>({ required: true });

defineProps({
  labels: {
    type: Array as () => MultiPurposeLabelOut[],
    required: true,
  },
  units: {
    type: Array as () => IngredientUnit[],
    required: true,
  },
  foods: {
    type: Array as () => IngredientFood[],
    required: true,
  },
});

defineEmits<{
  (e: "save"): void;
}>();

// The drawer only grows when "more options" is open; otherwise it's just the add field
const showDetails = ref(false);

const target = ref();
// Autocomplete menus are teleported outside the drawer, so selecting an item
// would otherwise register as an outside click and collapse the form
onClickOutside(target, () => showDetails.value = false, { ignore: [".v-overlay-container"] });
</script>
