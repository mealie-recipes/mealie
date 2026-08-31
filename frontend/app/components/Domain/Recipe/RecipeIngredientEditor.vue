<template>
  <div>
    <v-text-field
      v-if="model.title || showTitle"
      v-model="model.title"
      density="compact"
      variant="underlined"
      hide-details
      class="mx-1 mt-3 mb-4"
      :placeholder="$t('recipe.section-title')"
      style="max-width: 500px"
      @click="$emit('clickIngredientField', 'title')"
    />
    <RecipeIngredientEditorLayout :header="enableDragHandle || enableContextMenu">
      <template v-if="enableDragHandle" #dragHandle>
        <v-icon class="ma-2 handle" size="large">
          {{ $globals.icons.arrowUpDown }}
        </v-icon>
      </template>
      <template v-if="enableContextMenu" #contextMenu>
        <BaseButtonGroup
          hover
          :large="false"
          class="ml-auto"
          :buttons="btns"
          @toggle-section="toggleTitle"
          @toggle-subrecipe="toggleIsRecipe"
          @insert-above="$emit('insert-above')"
          @insert-below="$emit('insert-below')"
          @delete="$emit('delete')"
        />
      </template>
      <template #form>
        <div class="flex-grow-1">
          <div class="d-flex ga-2 py-2" :class="$vuetify.display.mdAndDown ? 'flex-column' : ''">
            <v-number-input
              v-model="model.quantity"
              variant="filled"
              :precision="null"
              :min="0"
              hide-details
              inset
              control-variant="stacked"
              density="compact"
              :style="$vuetify.display.mdAndDown ? '' : 'flex: 1 0 50px;'"
              :placeholder="$t('recipe.quantity')"
              @keypress="quantityFilter"
            />
            <v-autocomplete
              ref="unitAutocomplete"
              v-model="model.unit"
              v-model:search="unitSearch"
              auto-select-first
              hide-details
              density="compact"
              :style="$vuetify.display.mdAndDown ? '' : 'flex: 2 0 50px;'"
              variant="filled"
              return-object
              :items="filteredUnits"
              :custom-filter="() => true"
              item-title="name"
              :placeholder="$t('recipe.choose-unit')"
              clearable
              :menu-props="{ attach: props.menuAttachTarget, maxHeight: '250px' }"
              @keyup.enter="handleUnitEnter"
            >
              <template v-if="unitError" #prepend-inner>
                <v-tooltip location="bottom">
                  <template #activator="{ props: unitTooltipProps }">
                    <v-icon
                      v-bind="unitTooltipProps"
                      class="opacity-100"
                      color="primary"
                    >
                      {{ $globals.icons.alert }}
                    </v-icon>
                  </template>
                  <span v-if="unitErrorTooltip">
                    {{ unitErrorTooltip }}
                  </span>
                </v-tooltip>
              </template>
              <template #no-data>
                <div class="caption text-center pb-2">
                  {{ $t("recipe.press-enter-to-create") }}
                </div>
              </template>
              <template #append-item>
                <div v-if="showCreateUnit" class="px-2">
                  <BaseButton
                    block
                    size="small"
                    @click="createAssignUnit()"
                  />
                </div>
              </template>
            </v-autocomplete>

            <!-- Foods Input -->
            <v-autocomplete
              v-if="!state.isRecipe"
              ref="foodAutocomplete"
              v-model="model.food"
              v-model:search="foodSearch"
              auto-select-first
              hide-details
              density="compact"
              :style="$vuetify.display.mdAndDown ? '' : 'flex: 4 0 50px;'"
              variant="filled"
              return-object
              :items="filteredFoods"
              :custom-filter="() => true"
              item-title="name"
              :placeholder="$t('recipe.choose-food')"
              clearable
              :menu-props="{ attach: props.menuAttachTarget, maxHeight: '250px' }"
              @keyup.enter="handleFoodEnter"
            >
              <template v-if="foodError" #prepend-inner>
                <v-tooltip location="bottom">
                  <template #activator="{ props: foodTooltipProps }">
                    <v-icon
                      v-bind="foodTooltipProps"
                      class="opacity-100"
                      color="primary"
                    >
                      {{ $globals.icons.alert }}
                    </v-icon>
                  </template>
                  <span v-if="foodErrorTooltip">
                    {{ foodErrorTooltip }}
                  </span>
                </v-tooltip>
              </template>
              <template #no-data>
                <div class="caption text-center pb-2">
                  {{ $t("recipe.press-enter-to-create") }}
                </div>
              </template>
              <template #append-item>
                <div v-if="showCreateFood" class="px-2">
                  <BaseButton
                    block
                    size="small"
                    @click="createAssignFood()"
                  />
                </div>
              </template>
            </v-autocomplete>
            <!-- Recipe Input -->
            <v-autocomplete
              v-if="state.isRecipe"
              ref="search.query"
              v-model="model.referencedRecipe"
              v-model:search="search.query.value"
              auto-select-first
              hide-details
              density="compact"
              :style="$vuetify.display.mdAndDown ? '' : 'flex: 4 0 50px;'"
              variant="filled"
              return-object
              :items="search.data.value || []"
              item-title="name"
              :placeholder="$t('search.type-to-search')"
              clearable
              :label="!model.referencedRecipe ? $t('recipe.choose-recipe') : ''"
              @click="search.trigger()"
              @focus="search.trigger()"
            />
            <v-text-field
              v-model="model.note"
              hide-details
              density="compact"
              :style="$vuetify.display.mdAndDown ? '' : 'flex: 4 0 50px;'"
              variant="filled"
              :placeholder="$t('recipe.notes')"
              class=""
              @click="$emit('clickIngredientField', 'note')"
            />
          </div>
        </div>
      </template>
    </RecipeIngredientEditorLayout>
    <div class="px-2" :class="{ 'ml-10': !$vuetify.display.mdAndDown }">
      <slot name="before-divider" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#app";
import { computed, reactive, ref, toRefs, watch } from "vue";
import { useI18n } from "vue-i18n";
import { usePublicExploreApi, useUserApi } from "~/composables/api";
import { useRecipeSearch } from "~/composables/recipes/use-recipe-search";
import { useFoodData, useFoodStore, useUnitData, useUnitStore } from "~/composables/store";
import { useSearch } from "~/composables/use-search";
import type { RecipeIngredient } from "~/lib/api/types/recipe";

// defineModel replaces modelValue prop
const model = defineModel<RecipeIngredient>({ required: true });

const props = defineProps({
  menuAttachTarget: {
    type: String,
    default: "body",
  },
  isRecipe: {
    type: Boolean,
    default: false,
  },
  unitError: {
    type: Boolean,
    default: false,
  },
  unitErrorTooltip: {
    type: String,
    default: "",
  },
  foodError: {
    type: Boolean,
    default: false,
  },
  foodErrorTooltip: {
    type: String,
    default: "",
  },
  enableContextMenu: {
    type: Boolean,
    default: false,
  },
  enableDragHandle: {
    type: Boolean,
    default: false,
  },
  deleteDisabled: {
    type: Boolean,
    default: false,
  },
});

defineEmits([
  "clickIngredientField",
  "insert-above",
  "insert-below",
  "delete",
]);

const i18n = useI18n();
const { $globals } = useNuxtApp();

const state = reactive({
  showTitle: false,
  isRecipe: props.isRecipe,
});

const contextMenuOptions = computed(() => {
  const options = [
    {
      text: i18n.t("recipe.toggle-section"),
      event: "toggle-section",
    },
    {
      text: i18n.t("recipe.toggle-recipe"),
      event: "toggle-subrecipe",
    },
    {
      text: i18n.t("recipe.insert-above"),
      event: "insert-above",
    },
    {
      text: i18n.t("recipe.insert-below"),
      event: "insert-below",
    },
  ];

  return options;
});

const btns = computed(() => {
  const out = [
    {
      icon: $globals.icons.dotsVertical,
      text: i18n.t("general.menu"),
      event: "open",
      children: contextMenuOptions.value,
    },
  ];

  // If delete event is being listened for, show delete button
  // $attrs is not available in <script setup>, so always show if parent listens
  out.unshift({
    icon: $globals.icons.delete,
    text: i18n.t("general.delete"),
    event: "delete",
    children: undefined,
    disabled: props.deleteDisabled,
  });
  return out;
});

// Foods
const foodStore = useFoodStore();
const foodData = useFoodData();
const foodAutocomplete = ref<HTMLInputElement>();
const { search: foodSearch, filtered: filteredFoods } = useSearch(foodStore.store);

const showCreateFood = computed(() =>
  !!foodSearch.value
  && !filteredFoods.value.some((f: any) => (f.name ?? "").toLowerCase() === foodSearch.value.toLowerCase()),
);

async function createAssignFood() {
  foodData.data.name = foodSearch.value;
  model.value.food = await foodStore.actions.createOne(foodData.data) || undefined;
  foodData.reset();
  foodAutocomplete.value?.blur();
}

// Recipes
const route = useRoute();
const auth = useMealieAuth();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");

const { isOwnGroup } = useLoggedInState();
const api = isOwnGroup.value ? useUserApi() : usePublicExploreApi(groupSlug.value).explore;
const search = useRecipeSearch(api);
const loading = ref(false);
const selectedIndex = ref(-1);
// Reset or Grab Recipes on Change
watch(loading, (val) => {
  if (!val) {
    search.query.value = "";
    selectedIndex.value = -1;
    search.data.value = [];
  }
});

// Units
const unitStore = useUnitStore();
const unitsData = useUnitData();
const unitAutocomplete = ref<HTMLInputElement>();
const { search: unitSearch, filtered: filteredUnits } = useSearch(unitStore.store);

const showCreateUnit = computed(() =>
  !!unitSearch.value
  && !filteredUnits.value.some((u: any) => (u.name ?? "").toLowerCase() === unitSearch.value.toLowerCase()),
);

async function createAssignUnit() {
  unitsData.data.name = unitSearch.value;
  model.value.unit = await unitStore.actions.createOne(unitsData.data) || undefined;
  unitsData.reset();
  unitAutocomplete.value?.blur();
}

function toggleTitle() {
  if (state.showTitle) {
    model.value.title = "";
  }
  state.showTitle = !state.showTitle;
}

function toggleIsRecipe() {
  if (state.isRecipe) {
    model.value.referencedRecipe = undefined;
  }
  else {
    model.value.unit = undefined;
    model.value.food = undefined;
  }
  state.isRecipe = !state.isRecipe;
}

function handleUnitEnter() {
  if (
    model.value.unit === undefined
    || model.value.unit === null
    || !model.value.unit.name.includes(unitSearch.value)
  ) {
    createAssignUnit();
  }
}

function handleFoodEnter() {
  if (
    model.value.food === undefined
    || model.value.food === null
    || !model.value.food.name.includes(foodSearch.value)
  ) {
    createAssignFood();
  }
}

function quantityFilter(e: KeyboardEvent) {
  if (e.key === "-" || e.key === "+" || e.key === "e") {
    e.preventDefault();
  }
}

const { showTitle } = toRefs(state);
</script>
