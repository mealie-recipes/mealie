<template>
  <div class="d-flex flex-column ga-3">
    <v-combobox
      ref="inputRef"
      v-model="selected"
      v-model:search="search"
      :items="search ? filteredFoods : []"
      :item-title="foodName"
      return-object
      :custom-filter="() => true"
      :menu-props="{ location: menuDirection }"
      :label="$t('shopping-list.add-item')"
      :prepend-inner-icon="$globals.icons.foods"
      menu-icon=""
      variant="solo-filled"
      rounded
      clearable
      hide-details
      hide-no-data
      enterkeyhint="next"
      @update:model-value="onSelect"
      @keyup.enter="submit()"
      @blur="handleBlur"
    >
      <template #append-inner>
        <v-tooltip
          v-model="tooltipOpen"
          :text="tooltipText"
          location="top"
        >
          <template #activator="{ props: tooltipProps }">
            <v-btn
              v-bind="tooltipProps"
              :icon="$globals.icons.chevronDown"
              :class="{ 'quick-add-toggle--open': showDetails }"
              :aria-label="$t('shopping-list.more-options')"
              :aria-expanded="showDetails"
              variant="text"
              size="small"
              @click.stop="toggleDetails"
            />
          </template>
        </v-tooltip>
      </template>
    </v-combobox>

    <template v-if="showDetails">
      <ShoppingListItemDetails
        v-model="listItem"
        :labels="labels"
        :units="units"
        @save="submit()"
      />
      <div class="d-flex flex-wrap align-center ga-3">
        <BaseButton
          v-if="search?.trim() && !pickedFood && !resolveFood(search, foods)"
          size="small"
          color="info"
          :icon="$globals.icons.foods"
          :text="$t('shopping-list.save-as-new-food', { text: search.trim() })"
          @click="createFoodAndSubmit"
        />
        <v-spacer />
        <BaseButton
          save
          @click="submit()"
        />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useFoodName, useFoodPlurality } from "~/composables/recipes/use-recipe-ingredients";
import { resolveFood, useShoppingListItemEditor } from "~/composables/shopping-list-page/use-shopping-list-item-editor";
import { useSearch } from "~/composables/use-search";
import type { IngredientFood, ShoppingListItemOut } from "~/lib/api/types/household";
import type { MultiPurposeLabelOut } from "~/lib/api/types/labels";
import type { IngredientUnit } from "~/lib/api/types/recipe";
import ShoppingListItemDetails from "./ShoppingListItemDetails.vue";

const listItem = defineModel<ShoppingListItemOut>({ required: true });
const showDetails = defineModel<boolean>("details", { default: false });

const props = defineProps({
  foods: {
    type: Array as () => IngredientFood[],
    required: true,
  },
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

const i18n = useI18n();

const { createAssignFood } = useShoppingListItemEditor(listItem);

const { smAndDown } = useDisplay();
const menuDirection = computed(() => smAndDown.value ? "top" : "bottom");

const inputRef = ref<{ focus: () => void } | null>(null);
const selected = ref<IngredientFood | string | null>(null);
const tooltipOpen = ref(false);
const tooltipText = ref("");

// The wording is fixed when the tooltip opens, and the tooltip hides on toggle, so the text never
// changes while it's visible or fading out; the next hover shows the new wording
watch(tooltipOpen, (open) => {
  if (open) {
    tooltipText.value = showDetails.value ? i18n.t("shopping-list.fewer-options") : i18n.t("shopping-list.more-options");
  }
});

function toggleDetails() {
  showDetails.value = !showDetails.value;
  tooltipOpen.value = false;
}
const { search, filtered: filteredFoods } = useSearch(computed(() => props.foods));

// Show suggestions the way the list will display the new item (no quantity or unit)
const { shouldPluralizeFood } = useFoodPlurality();
const usePlural = computed(() => shouldPluralizeFood({ quantity: 0 }));
function foodName(food: IngredientFood | string) {
  return typeof food === "string" ? food : useFoodName(food, usePlural.value);
}

// Picking a suggestion is an explicit choice of that food; typing only updates the model with a string
const pickedFood = computed(() => selected.value && typeof selected.value === "object" ? selected.value : undefined);

// With the options open, picking a food only fills it in so the other fields can still be set before saving
function onSelect() {
  if (pickedFood.value && !showDetails.value) {
    submit();
  }
}

function handleBlur() {
  // Select the first filtered item when focus leaves the field
  // This handles mobile "next" button which typically only fires blur, not Enter
  if (search.value && !selected.value && filteredFoods.value.length > 0) {
    selected.value = filteredFoods.value[0];
  }
}

// Free text is a food only on an exact match; anything else is kept verbatim as a note,
// combined with anything typed in the note field
function submit(createdFood?: IngredientFood) {
  const text = search.value?.trim() || "";
  const food = createdFood ?? pickedFood.value ?? resolveFood(text, props.foods);
  const note = food ? listItem.value.note : [text, listItem.value.note].filter(Boolean).join(", ");
  if (!food && !note) {
    return;
  }

  listItem.value.food = food;
  listItem.value.foodId = food?.id;
  if (food && !listItem.value.labelId) {
    listItem.value.label = food.label;
    listItem.value.labelId = food.labelId;
  }
  listItem.value.note = note;
  listItem.value.quantity ||= 0;
  emit("save");

  selected.value = null;
  search.value = "";
  inputRef.value?.focus();
}

async function createFoodAndSubmit() {
  await createAssignFood(search.value.trim());
  if (listItem.value.foodId) {
    submit(listItem.value.food as IngredientFood);
  }
}
</script>

<style scoped>
.quick-add-toggle--open {
  transform: rotate(180deg);
}
</style>
