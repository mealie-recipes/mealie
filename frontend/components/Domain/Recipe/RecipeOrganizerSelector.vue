<template>
  <v-autocomplete
    v-model="selected"
    v-bind="inputAttrs"
    v-model:search="searchInput"
    :items="items"
    :label="label"
    chips
    closable-chips
    item-title="name"
    multiple
    :variant="variant"
    :prepend-inner-icon="icon"
    :append-icon="showAdd ? $globals.icons.create : undefined"
    return-object
    auto-select-first
    class="pa-0"
    @update:model-value="resetSearchInput"
    @click:append="dialog = true"
  >
    <template #chip="{ item, index }">
      <v-chip
        :key="index"
        class="ma-1"
        color="accent"
        variant="flat"
        label

        closable
        @click:close="removeByIndex(index)"
      >
        {{ item.value }}
      </v-chip>
    </template>

    <template
      v-if="showAdd"
      #append
    >
      <RecipeOrganizerDialog
        v-model="dialog"
        :item-type="selectorType"
        @created-item="appendCreated"
      />
    </template>
  </v-autocomplete>
</template>

<script setup lang="ts">
import type { IngredientFood, RecipeCategory, RecipeTag } from "~/lib/api/types/recipe";
import type { RecipeTool } from "~/lib/api/types/admin";
import { Organizer, type RecipeOrganizer } from "~/lib/api/types/non-generated";
import type { HouseholdSummary } from "~/lib/api/types/household";
import { useCategoryStore, useFoodStore, useHouseholdStore, useTagStore, useToolStore } from "~/composables/store";

interface Props {
  selectorType: RecipeOrganizer;
  inputAttrs?: Record<string, any>;
  returnObject?: boolean;
  showAdd?: boolean;
  showLabel?: boolean;
  showIcon?: boolean;
  variant?: "filled" | "underlined" | "outlined" | "plain" | "solo" | "solo-inverted" | "solo-filled";
}

const props = withDefaults(defineProps<Props>(), {
  inputAttrs: () => ({}),
  returnObject: true,
  showAdd: true,
  showLabel: true,
  showIcon: true,
  variant: "outlined",
});

const selected = defineModel<(
  | HouseholdSummary
  | RecipeTag
  | RecipeCategory
  | RecipeTool
  | IngredientFood
  | string
)[] | undefined>({ required: true });

onMounted(() => {
  if (selected.value === undefined) {
    selected.value = [];
  }
});

const i18n = useI18n();
const { $globals } = useNuxtApp();

const label = computed(() => {
  if (!props.showLabel) {
    return "";
  }

  switch (props.selectorType) {
    case Organizer.Tag:
      return i18n.t("tag.tags");
    case Organizer.Category:
      return i18n.t("category.categories");
    case Organizer.Tool:
      return i18n.t("tool.tools");
    case Organizer.Food:
      return i18n.t("general.foods");
    case Organizer.Household:
      return i18n.t("household.households");
    default:
      return i18n.t("general.organizer");
  }
});

const icon = computed(() => {
  if (!props.showIcon) {
    return "";
  }

  switch (props.selectorType) {
    case Organizer.Tag:
      return $globals.icons.tags;
    case Organizer.Category:
      return $globals.icons.categories;
    case Organizer.Tool:
      return $globals.icons.tools;
    case Organizer.Food:
      return $globals.icons.foods;
    case Organizer.Household:
      return $globals.icons.household;
    default:
      return $globals.icons.tags;
  }
});

// ===========================================================================
// Store & Items Setup

const storeMap = {
  [Organizer.Category]: useCategoryStore(),
  [Organizer.Tag]: useTagStore(),
  [Organizer.Tool]: useToolStore(),
  [Organizer.Food]: useFoodStore(),
  [Organizer.Household]: useHouseholdStore(),
};

const store = computed(() => {
  const { store } = storeMap[props.selectorType];
  return store.value;
});

const items = computed(() => {
  if (!props.returnObject) {
    return store.value.map(item => item.name);
  }
  return store.value;
});

function removeByIndex(index: number) {
  if (selected.value === undefined) {
    return;
  }
  const newSelected = selected.value.filter((_, i) => i !== index);
  selected.value = [...newSelected];
}

function appendCreated(item: any) {
  if (selected.value === undefined) {
    return;
  }

  selected.value = [...selected.value, item];
}

const dialog = ref(false);

const searchInput = ref("");

function resetSearchInput() {
  searchInput.value = "";
}
</script>

<style scoped>
.v-autocomplete {
  /* This aligns the input with other standard input fields */
  margin-top: 6px;
}
</style>
