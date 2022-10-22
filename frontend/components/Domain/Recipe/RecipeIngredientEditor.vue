<template>
  <div>
    <v-text-field
      v-if="value.title || showTitle"
      v-model="value.title"
      dense
      hide-details
      class="mx-1 mt-3 mb-4"
      :placeholder="$t('recipe.section-title')"
      style="max-width: 500px"
      @click="$emit('clickIngredientField', 'title')"
    >
    </v-text-field>
    <v-row :no-gutters="$vuetify.breakpoint.mdAndUp" dense class="d-flex flex-wrap my-1">
      <v-col v-if="!disableAmount" sm="12" md="2" cols="12" class="flex-grow-0 flex-shrink-0">
        <v-text-field
          v-model="value.quantity"
          solo
          hide-details
          dense
          class="mx-1"
          type="number"
          :placeholder="$t('recipe.quantity')"
          @keypress="quantityFilter"
        >
          <v-icon v-if="$listeners && $listeners.delete" slot="prepend" class="mr-n1 handle">
            {{ $globals.icons.arrowUpDown }}
          </v-icon>
        </v-text-field>
      </v-col>
      <v-col v-if="!disableAmount" sm="12" md="3" cols="12">
        <v-autocomplete
          v-model="value.unit"
          :search-input.sync="unitSearch"
          hide-details
          dense
          solo
          return-object
          :items="units || []"
          item-text="name"
          class="mx-1"
          :placeholder="$t('recipe.choose-unit')"
          clearable
          @keyup.enter="handleUnitEnter"
        >
          <template #no-data>
            <div class="caption text-center pb-2">{{ $t("recipe.press-enter-to-create") }}</div>
          </template>
          <template #append-item>
            <div class="px-2">
              <BaseButton block small @click="createAssignUnit()"></BaseButton>
            </div>
          </template>
        </v-autocomplete>
      </v-col>

      <!-- Foods Input -->
      <v-col v-if="!disableAmount" m="12" md="3" cols="12" class="">
        <v-autocomplete
          v-model="value.food"
          :search-input.sync="foodSearch"
          hide-details
          dense
          solo
          return-object
          :items="foods || []"
          item-text="name"
          class="mx-1 py-0"
          :placeholder="$t('recipe.choose-food')"
          clearable
          @keyup.enter="handleFoodEnter"
        >
          <template #no-data>
            <div class="caption text-center pb-2">{{ $t("recipe.press-enter-to-create") }}</div>
          </template>
          <template #append-item>
            <div class="px-2">
              <BaseButton block small @click="createAssignFood()"></BaseButton>
            </div>
          </template>
        </v-autocomplete>
      </v-col>
      <v-col sm="12" md="" cols="12">
        <div class="d-flex">
          <v-text-field
            v-model="value.note"
            hide-details
            dense
            solo
            class="mx-1"
            :placeholder="$t('recipe.notes')"
            @click="$emit('clickIngredientField', 'note')"
          >
            <v-icon v-if="disableAmount && $listeners && $listeners.delete" slot="prepend" class="mr-n1 handle">
              {{ $globals.icons.arrowUpDown }}
            </v-icon>
          </v-text-field>
          <BaseButtonGroup
            hover
            :large="false"
            class="my-auto"
            :buttons="[
              {
                icon: $globals.icons.delete,
                text: $tc('general.delete'),
                event: 'delete',
              },
              {
                icon: $globals.icons.dotsVertical,
                text: $tc('general.menu'),
                event: 'open',
                children: contextMenuOptions,
              },
            ]"
            @toggle-section="toggleTitle"
            @toggle-original="toggleOriginalText"
            @delete="$emit('delete')"
          />
        </div>
      </v-col>
    </v-row>
    <p v-if="showOriginalText" class="text-caption">
      {{ $t("recipe.original-text-with-value", { originalText: value.originalText }) }}
    </p>

    <v-divider v-if="!$vuetify.breakpoint.mdAndUp" class="my-4"></v-divider>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, useContext } from "@nuxtjs/composition-api";
import { useFoodStore, useFoodData, useUnitStore, useUnitData } from "~/composables/store";
import { validators } from "~/composables/use-validators";
import { RecipeIngredient } from "~/lib/api/types/recipe";

export default defineComponent({
  props: {
    value: {
      type: Object as () => RecipeIngredient,
      required: true,
    },
    disableAmount: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const { i18n } = useContext();

    // ==================================================
    // Foods
    const foodStore = useFoodStore();
    const foodData = useFoodData();
    const foodSearch = ref("");

    async function createAssignFood() {
      foodData.data.name = foodSearch.value;
      await foodStore.actions.createOne(foodData.data);
      props.value.food = foodStore.foods.value?.find((food) => food.name === foodSearch.value);
      foodData.reset();
    }

    // ==================================================
    // Units
    const unitStore = useUnitStore();
    const unitsData = useUnitData();
    const unitSearch = ref("");

    async function createAssignUnit() {
      unitsData.data.name = unitSearch.value;
      await unitStore.actions.createOne(unitsData.data);
      props.value.unit = unitStore.units.value?.find((unit) => unit.name === unitSearch.value);
      unitsData.reset();
    }

    const state = reactive({
      showTitle: false,
      showOriginalText: false,
    });

    function toggleTitle() {
      if (state.showTitle) {
        props.value.title = "";
      }
      state.showTitle = !state.showTitle;
    }

    function toggleOriginalText() {
      state.showOriginalText = !state.showOriginalText;
    }

    function handleUnitEnter() {
      if (
        props.value.unit === undefined ||
        props.value.unit === null ||
        !props.value.unit.name.includes(unitSearch.value)
      ) {
        createAssignUnit();
      }
    }

    function handleFoodEnter() {
      if (
        props.value.food === undefined ||
        props.value.food === null ||
        !props.value.food.name.includes(foodSearch.value)
      ) {
        createAssignFood();
      }
    }

    const contextMenuOptions = computed(() => {
      const options = [
        {
          text: i18n.t("recipe.toggle-section") as string,
          event: "toggle-section",
        },
      ];

      // FUTURE: add option to parse a single ingredient
      // if (!value.food && !value.unit && value.note) {
      //   options.push({
      //     text: "Parse Ingredient",
      //     event: "parse-ingredient",
      //   });
      // }

      if (props.value.originalText) {
        options.push({
          text: i18n.t("recipe.see-original-text") as string,
          event: "toggle-original",
        });
      }

      return options;
    });

    function quantityFilter(e: KeyboardEvent) {
      // if digit is pressed, add to quantity
      if (e.key === "-" || e.key === "+" || e.key === "e") {
        e.preventDefault();
      }
    }

    return {
      ...toRefs(state),
      quantityFilter,
      toggleOriginalText,
      contextMenuOptions,
      handleUnitEnter,
      handleFoodEnter,
      createAssignFood,
      createAssignUnit,
      foods: foodStore.foods,
      foodSearch,
      toggleTitle,
      unitActions: unitStore.actions,
      units: unitStore.units,
      unitSearch,
      validators,
      workingUnitData: unitsData.data,
    };
  },
});
</script>

<style>
.v-input__append-outer {
  margin: 0 !important;
  padding: 0 !important;
}
</style>
