<template>
  <div class="d-flex ga-3">
    <v-number-input
      v-model="listItem.quantity"
      hide-details
      :label="$t('form.quantity-label-abbreviated')"
      :min="0"
      :precision="null"
      control-variant="stacked"
      style="flex: 1"
      inset
    />
    <InputLabelType
      v-model="listItem.unit"
      v-model:item-id="listItem.unitId!"
      :items="units"
      :label="$t('recipe.unit')"
      :icon="$globals.icons.units"
      :menu-props="{ location: menuDirection }"
      style="flex: 3"
      create
      @create="createAssignUnit"
    />
  </div>
  <v-textarea
    v-model="listItem.note"
    hide-details
    :label="$t('shopping-list.note')"
    rows="1"
    auto-grow
    @keypress="handleNoteKeyPress"
  />
  <div class="d-flex flex-wrap align-end ga-3">
    <InputLabelType
      v-model="listItem.label"
      v-model:item-id="listItem.labelId!"
      :items="labels"
      :label="$t('shopping-list.label')"
      :menu-props="{ location: menuDirection }"
      style="flex: 1 0 200px"
    />
    <BaseButton
      v-if="listItem.labelId && listItem.food && listItem.labelId !== listItem.food.labelId"
      small
      color="info"
      :icon="$globals.icons.tagArrowRight"
      :text="$t('shopping-list.save-label')"
      class="mt-2 align-items-flex-start"
      style="flex-grow: 0"
      @click="assignLabelToFood"
    />
    <v-spacer />
  </div>
</template>

<script setup lang="ts">
import { useShoppingListItemEditor } from "~/composables/shopping-list-page/use-shopping-list-item-editor";
import type { ShoppingListItemCreate, ShoppingListItemOut } from "~/lib/api/types/household";
import type { MultiPurposeLabelOut } from "~/lib/api/types/labels";
import type { IngredientUnit } from "~/lib/api/types/recipe";

// modelValue as reactive v-model
const listItem = defineModel<ShoppingListItemCreate | ShoppingListItemOut>({ required: true });

defineProps({
  labels: {
    type: Array as () => MultiPurposeLabelOut[],
    required: true,
  },
  units: {
    type: Array as () => IngredientUnit[],
    required: true,
  },
});

const emit = defineEmits<{ (e: "save"): void }>();

const { assignLabelToFood, createAssignUnit } = useShoppingListItemEditor(listItem);

const { smAndDown } = useDisplay();
const menuDirection = computed(() => smAndDown.value ? "top" : "bottom");

function handleNoteKeyPress(event: KeyboardEvent) {
  // Save on Enter
  if (!event.shiftKey && event.key === "Enter") {
    event.preventDefault();
    emit("save");
  }
}
</script>
