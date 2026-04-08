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

<script setup lang="ts">
import type { MultiPurposeLabelSummary } from "~/lib/api/types/labels";
import type { IngredientFood, IngredientUnit } from "~/lib/api/types/recipe";
import { useSearch } from "~/composables/use-search";

// v-model for the selected item
const modelValue = defineModel<MultiPurposeLabelSummary | IngredientFood | IngredientUnit | null>({ default: () => null });

// support v-model:item-id binding
const itemId = defineModel<string | undefined>("item-id", { default: undefined });

const props = defineProps({
  items: {
    type: Array as () => Array<MultiPurposeLabelSummary | IngredientFood | IngredientUnit>,
    required: true,
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
});

const emit = defineEmits<{
  (e: "create", val: string): void;
}>();

const autocompleteRef = ref<HTMLInputElement>();

// Use the search composable
const { search: searchInput, filtered: filteredItems } = useSearch(computed(() => props.items));

const itemVal = computed({
  get: () => {
    if (!modelValue.value || Object.keys(modelValue.value).length === 0) {
      return null;
    }
    return modelValue.value;
  },
  set: (val) => {
    itemId.value = val?.id || "";
    modelValue.value = val;
  },
});

function emitCreate() {
  if (props.items.some(item => item.name === searchInput.value)) {
    return;
  }
  emit("create", searchInput.value);
  autocompleteRef.value?.blur();
}
</script>
