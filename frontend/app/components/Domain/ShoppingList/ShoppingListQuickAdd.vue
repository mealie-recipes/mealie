<template>
  <v-combobox
    ref="inputRef"
    v-model="selected"
    v-model:search="search"
    :items="search ? filteredFoods : []"
    :item-title="foodName"
    return-object
    :custom-filter="() => true"
    :label="$t('shopping-list.add-item')"
    :prepend-inner-icon="$globals.icons.foods"
    menu-icon=""
    variant="solo-filled"
    rounded
    clearable
    hide-details
    hide-no-data
    @update:model-value="onSelect"
    @keyup.enter="submitText"
  />
</template>

<script setup lang="ts">
import { useFoodName, useFoodPlurality } from "~/composables/recipes/use-recipe-ingredients";
import { resolveFood } from "~/composables/shopping-list-page/use-shopping-list-item-editor";
import { useSearch } from "~/composables/use-search";
import type { IngredientFood, ShoppingListItemOut } from "~/lib/api/types/household";

const listItem = defineModel<ShoppingListItemOut>({ required: true });

const props = defineProps({
  foods: {
    type: Array as () => IngredientFood[],
    required: true,
  },
});

const emit = defineEmits<{ (e: "save"): void }>();

const inputRef = ref<{ focus: () => void } | null>(null);
const selected = ref<IngredientFood | string | null>(null);
const { search, filtered: filteredFoods } = useSearch(computed(() => props.foods));

// Show suggestions the way the list will display the new item (no quantity or unit)
const { shouldPluralizeFood } = useFoodPlurality();
const usePlural = computed(() => shouldPluralizeFood({ quantity: 0 }));
function foodName(food: IngredientFood | string) {
  return typeof food === "string" ? food : useFoodName(food, usePlural.value);
}

// Picking a suggestion is an explicit choice of that food; typing only updates the model with a string
function onSelect(val: IngredientFood | string | null) {
  if (val && typeof val === "object") {
    save(val, "");
  }
}

// Free text is a food only on an exact match; anything else is kept verbatim as a note
function submitText() {
  const text = search.value?.trim();
  if (!text) {
    return;
  }

  const food = resolveFood(text, props.foods);
  save(food, food ? "" : text);
}

function save(food: IngredientFood | undefined, note: string) {
  listItem.value.food = food;
  listItem.value.foodId = food?.id;
  listItem.value.label = food?.label;
  listItem.value.labelId = food?.labelId;
  listItem.value.note = note;
  emit("save");

  selected.value = null;
  search.value = "";
  inputRef.value?.focus();
}
</script>
