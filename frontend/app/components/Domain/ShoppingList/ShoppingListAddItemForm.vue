<template>
  <v-navigation-drawer
    permanent
    rounded="t-xl"
    location="bottom"
    class="pa-4 pt-2 mb-0"
    width="300"
    rail-width="85"
    :rail="rail"
    elevation="4"
  >
    <div class="d-flex flex-column ga-3">
      <v-card-actions class="pa-0">
        <div class="position-relative" style="flex: 1;">
          <InputLabelType
            ref="foodInputRef"
            v-model="listItem.food"
            v-model:item-id="listItem.foodId!"
            :items="foods"
            :label="rail ? $t('shopping-list.add-item') : $t('shopping-list.food')"
            :icon="$globals.icons.foods"
            :style="rail ? 'margin-inline: 3px;' : undefined"
            :search="rail"
            :menu-props="{ location: menuDirection }"
            create
            @create="createAssignFood"
          />
          <!-- Intercept clicks when collapsed so the drawer expands before the autocomplete opens -->
          <div
            v-if="rail"
            class="position-absolute"
            style="inset: 0; cursor: text;"
            @click="expandAndFocus"
          />
        </div>
        <BaseButtonGroup
          v-if="!rail"
          :buttons="[
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
          @cancel="rail = true; $emit('cancel')"
        />
      </v-card-actions>

      <ShoppingListItemDetails
        v-if="!rail"
        v-model="listItem"
        :labels="labels"
        :units="units"
        @save="$emit('save')"
      />
    </div>
  </v-navigation-drawer>
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
});

defineEmits<{
  (e: "save" | "cancel" | "delete"): void;
}>();

const { createAssignFood } = useShoppingListItemEditor(listItem);

const { smAndDown } = useDisplay();
const menuDirection = computed(() => smAndDown.value ? "top" : "bottom");

const foodInputRef = ref<{ focus: () => void } | null>(null);
const rail = ref(true);

async function expandAndFocus() {
  rail.value = false;
  await nextTick();
  setTimeout(() => {
    foodInputRef.value?.focus();
  }, 200);
}

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
</script>
