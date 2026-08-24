<template>
  <v-card variant="elevated" class="pa-2" border="primary s-lg opacity-100">
    <div class="d-flex flex-column ga-3">
      <InputLabelType
        v-model="listItem.food"
        v-model:item-id="listItem.foodId!"
        :items="foods"
        :label="$t('shopping-list.food')"
        :icon="$globals.icons.foods"
        :autofocus="autoFocus === 'food'"
        create
        @create="createAssignFood"
      />
      <ShoppingListItemDetails
        v-model="listItem"
        :labels="labels"
        :units="units"
        @save="$emit('save')"
      />
    </div>
    <v-card-actions class="justify-end pa-0">
      <BaseButtonGroup
        :buttons="[
          ...(allowDelete
            ? [
              {
                icon: $globals.icons.delete,
                text: $t('general.delete'),
                event: 'delete',
              },
            ]
            : []),
          {
            icon: $globals.icons.close,
            text: $t('general.cancel'),
            event: 'cancel',
          },
          {
            icon: $globals.icons.save,
            text: $t('general.save'),
            event: 'save',
          },
        ]"
        @save="$emit('save')"
        @cancel="$emit('cancel')"
        @delete="$emit('delete')"
      />
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { useShoppingListItemEditor } from "~/composables/shopping-list-page/use-shopping-list-item-editor";
import type { ShoppingListItemCreate, ShoppingListItemOut } from "~/lib/api/types/household";
import type { MultiPurposeLabelOut } from "~/lib/api/types/labels";
import type { IngredientFood, IngredientUnit } from "~/lib/api/types/recipe";
import ShoppingListItemDetails from "./ShoppingListItemDetails.vue";

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
  foods: {
    type: Array as () => IngredientFood[],
    required: true,
  },
  allowDelete: {
    type: Boolean,
    required: false,
    default: true,
  },
});

// const emit = defineEmits<["save", "cancel", "delete"]>();
defineEmits<{
  (e: "save" | "cancel" | "delete"): void;
}>();

const { createAssignFood } = useShoppingListItemEditor(listItem);

watch(
  () => listItem.value.quantity,
  (newQty) => {
    if (!newQty) {
      listItem.value.quantity = 0;
    }
  },
);

watch(
  () => listItem.value.food,
  (newFood) => {
    listItem.value.label = newFood?.label || null;
    listItem.value.labelId = listItem.value.label?.id || null;
  },
);

const autoFocus = computed(() => (!listItem.value.food && listItem.value.note ? "note" : "food"));
</script>
