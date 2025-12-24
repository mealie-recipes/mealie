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
    <v-row
      :no-gutters="mdAndUp"
      dense
      class="d-flex flex-wrap my-1"
    >
      <v-col
        sm="12"
        md="2"
        cols="12"
        class="flex-grow-0 flex-shrink-0"
      >
        <v-number-input
          v-model="model.quantity"
          variant="solo"
          :precision="null"
          :min="0"
          hide-details
          control-variant="stacked"
          inset
          density="compact"
          :placeholder="$t('recipe.quantity')"
          @keypress="quantityFilter"
        >
          <template v-if="enableDragHandle" #prepend>
            <v-icon
              class="mr-n1 handle"
            >
              {{ $globals.icons.arrowUpDown }}
            </v-icon>
          </template>
        </v-number-input>
      </v-col>
      <v-col
        v-if="!state.isRecipe"
        sm="12"
        md="3"
        cols="12"
      >
        <v-autocomplete
          ref="unitAutocomplete"
          v-model="model.unit"
          v-model:search="unitSearch"
          auto-select-first
          hide-details
          density="compact"
          variant="solo"
          return-object
          :items="units || []"
          :custom-filter="normalizeFilter"
          item-title="name"
          class="mx-1"
          :placeholder="$t('recipe.choose-unit')"
          clearable
          :menu-props="{ attach: props.menuAttachTarget, maxHeight: '250px' }"
          @keyup.enter="handleUnitEnter"
        >
          <template #prepend>
            <v-tooltip v-if="unitError" location="bottom">
              <template #activator="{ props: unitTooltipProps }">
                <v-icon
                  v-bind="unitTooltipProps"
                  class="ml-2 mr-n3 opacity-100"
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
            <div class="px-2">
              <BaseButton
                block
                size="small"
                @click="createAssignUnit()"
              />
            </div>
          </template>
        </v-autocomplete>
      </v-col>

      <!-- Foods Input -->
      <v-col
        v-if="!state.isRecipe"
        m="12"
        md="3"
        cols="12"
        class=""
      >
        <v-autocomplete
          ref="foodAutocomplete"
          v-model="model.food"
          v-model:search="foodSearch"
          auto-select-first
          hide-details
          density="compact"
          variant="solo"
          return-object
          :items="foods || []"
          :custom-filter="normalizeFilter"
          item-title="name"
          class="mx-1 py-0"
          :placeholder="$t('recipe.choose-food')"
          clearable
          :menu-props="{ attach: props.menuAttachTarget, maxHeight: '250px' }"
          @keyup.enter="handleFoodEnter"
        >
          <template #prepend>
            <v-tooltip v-if="foodError" location="bottom">
              <template #activator="{ props: foodTooltipProps }">
                <v-icon
                  v-bind="foodTooltipProps"
                  class="ml-2 mr-n3 opacity-100"
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
            <div class="px-2">
              <BaseButton
                block
                size="small"
                @click="createAssignFood()"
              />
            </div>
          </template>
        </v-autocomplete>
      </v-col>
      <!-- Recipe Input -->
      <v-col
        v-if="state.isRecipe"
        m="12"
        md="6"
        cols="12"
        class=""
      >
        <v-autocomplete
          ref="search.query"
          v-model="model.referencedRecipe"
          v-model:search="search.query.value"
          auto-select-first
          hide-details
          density="compact"
          variant="solo"
          return-object
          :items="search.data.value || []"
          :custom-filter="normalizeFilter"
          item-title="name"
          class="mx-1 py-0"
          :placeholder="$t('search.type-to-search')"
          clearable
          :label="!model.referencedRecipe ? $t('recipe.choose-recipe') : ''"
          @click="search.trigger()"
          @focus="search.trigger()"
        >
          <template #prepend />
        </v-autocomplete>
      </v-col>
      <v-col
        sm="12"
        md=""
        cols="12"
      >
        <div class="d-flex">
          <v-text-field
            v-model="model.note"
            hide-details
            density="compact"
            variant="solo"
            :placeholder="$t('recipe.notes')"
            class="mb-auto"
            @click="$emit('clickIngredientField', 'note')"
          />
          <BaseButtonGroup
            v-if="enableContextMenu"
            hover
            :large="false"
            class="my-auto d-flex"
            :buttons="btns"
            @toggle-section="toggleTitle"
            @toggle-subrecipe="toggleIsRecipe"
            @insert-above="$emit('insert-above')"
            @insert-below="$emit('insert-below')"
            @delete="$emit('delete')"
          />
        </div>
      </v-col>
    </v-row>
    <slot name="before-divider" />
    <v-divider
      v-if="!mdAndUp"
      class="my-4"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, toRefs } from "vue";
import { useDisplay } from "vuetify";
import { useI18n } from "vue-i18n";
import { useFoodStore, useFoodData, useUnitStore, useUnitData } from "~/composables/store";
import { normalizeFilter } from "~/composables/use-utils";
import { useNuxtApp } from "#app";
import type { RecipeIngredient } from "~/lib/api/types/recipe";
import { usePublicExploreApi, useUserApi } from "~/composables/api";
import { useRecipeSearch } from "~/composables/recipes/use-recipe-search";

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

const { mdAndUp } = useDisplay();
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
const foodSearch = ref("");
const foodAutocomplete = ref<HTMLInputElement>();

async function createAssignFood() {
  foodData.data.name = foodSearch.value;
  model.value.food = await foodStore.actions.createOne(foodData.data) || undefined;
  foodData.reset();
  foodAutocomplete.value?.blur();
}

// Recipes
const route = useRoute();
const $auth = useMealieAuth();
const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");

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
const unitSearch = ref("");
const unitAutocomplete = ref<HTMLInputElement>();

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

const foods = foodStore.store;
const units = unitStore.store;
</script>

<style>
.v-input__append-outer {
  margin: 0 !important;
  padding: 0 !important;
}
</style>
