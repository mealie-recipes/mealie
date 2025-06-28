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
        v-if="!disableAmount"
        sm="12"
        md="2"
        cols="12"
        class="flex-grow-0 flex-shrink-0"
      >
        <v-text-field
          v-model="model.quantity"
          variant="solo"
          hide-details
          density="compact"
          type="number"
          :placeholder="$t('recipe.quantity')"
          @keypress="quantityFilter"
        >
          <template #prepend>
            <v-icon
              class="mr-n1 handle"
            >
              {{ $globals.icons.arrowUpDown }}
            </v-icon>
          </template>
        </v-text-field>
      </v-col>
      <v-col
        v-if="!disableAmount"
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
          item-title="name"
          class="mx-1"
          :placeholder="$t('recipe.choose-unit')"
          clearable
          @keyup.enter="handleUnitEnter"
        >
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
        v-if="!disableAmount"
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
          item-title="name"
          class="mx-1 py-0"
          :placeholder="$t('recipe.choose-food')"
          clearable
          @keyup.enter="handleFoodEnter"
        >
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
          >
            <template #prepend>
              <v-icon
                v-if="disableAmount && $attrs && $attrs.delete"
                class="mr-n1 handle"
              >
                {{ $globals.icons.arrowUpDown }}
              </v-icon>
            </template>
          </v-text-field>
          <BaseButtonGroup
            hover
            :large="false"
            class="my-auto d-flex"
            :buttons="btns"
            @toggle-section="toggleTitle"
            @toggle-original="toggleOriginalText"
            @insert-above="$emit('insert-above')"
            @insert-below="$emit('insert-below')"
            @insert-ingredient="$emit('insert-ingredient')"
            @delete="$emit('delete')"
          />
        </div>
      </v-col>
    </v-row>
    <p
      v-if="showOriginalText"
      class="text-caption"
    >
      {{ $t("recipe.original-text-with-value", { originalText: model.originalText }) }}
    </p>

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
import { useNuxtApp } from "#app";
import type { RecipeIngredient } from "~/lib/api/types/recipe";

// defineModel replaces modelValue prop
const model = defineModel<RecipeIngredient>({ required: true });

const props = defineProps({
  disableAmount: {
    type: Boolean,
    default: false,
  },
  allowInsertIngredient: {
    type: Boolean,
    default: false,
  },
});

defineEmits([
  "clickIngredientField",
  "insert-above",
  "insert-below",
  "insert-ingredient",
  "delete",
]);

const { mdAndUp } = useDisplay();
const i18n = useI18n();
const { $globals } = useNuxtApp();

const state = reactive({
  showTitle: false,
  showOriginalText: false,
});

const contextMenuOptions = computed(() => {
  const options = [
    {
      text: i18n.t("recipe.toggle-section"),
      event: "toggle-section",
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

  if (props.allowInsertIngredient) {
    options.push({
      text: i18n.t("recipe.insert-ingredient"),
      event: "insert-ingredient",
    });
  }

  if (model.value.originalText) {
    options.push({
      text: i18n.t("recipe.see-original-text"),
      event: "toggle-original",
    });
  }

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

function toggleOriginalText() {
  state.showOriginalText = !state.showOriginalText;
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

const { showTitle, showOriginalText } = toRefs(state);

const foods = foodStore.store;
const units = unitStore.store;
</script>

<style>
.v-input__append-outer {
  margin: 0 !important;
  padding: 0 !important;
}
</style>
