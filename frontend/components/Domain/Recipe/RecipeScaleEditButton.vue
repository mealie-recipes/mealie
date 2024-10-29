<template>
  <div>
    <div class="text-center d-flex align-center">
      <div>
        <v-menu v-model="menu" :disabled="!editScale" offset-y top nudge-top="6" :close-on-content-click="false">
          <template #activator="{ on, attrs }">
            <v-card class="pa-1 px-2" dark color="secondary darken-1" small v-bind="attrs" v-on="on">
              <span v-if="!recipeYield"> x {{ scale }} </span>
              <div v-else-if="!numberParsed && recipeYield">
                <span v-if="numerator === 1"> {{ recipeYield }} </span>
                <span v-else> {{ numerator }}x {{ scaledYield }} </span>
              </div>
              <span v-else> {{ scaledYield }} </span>

            </v-card>
          </template>
          <v-card min-width="300px">
            <v-card-title class="mb-0">
              {{ $t("recipe.servings") }}
            </v-card-title>
            <v-card-text class="mt-n5">
              <div class="mt-4 d-flex align-center">
                <v-text-field v-model="numerator" type="number" :min="0" hide-spin-buttons />
                <v-tooltip right color="secondary darken-1">
                  <template #activator="{ on, attrs }">
                    <v-btn v-bind="attrs" icon class="mx-1" small v-on="on" @click="scale = 1">
                      <v-icon>
                        {{ $globals.icons.undo }}
                      </v-icon>
                    </v-btn>
                  </template>
                  <span> {{ $t("recipe.reset-servings-count") }} </span>
                </v-tooltip>
              </div>
            </v-card-text>
          </v-card>
        </v-menu>
      </div>
      <BaseButtonGroup
        v-if="editScale"
        class="pl-2"
        :large="false"
        :buttons="[
          {
            icon: $globals.icons.minus,
            text: $tc('recipe.decrease-scale-label'),
            event: 'decrement',
            disabled: disableDecrement,
          },
          {
            icon: $globals.icons.createAlt,
            text: $tc('recipe.increase-scale-label'),
            event: 'increment',
          },
        ]"
        @decrement="numerator--"
        @increment="numerator++"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, watch  } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    recipeYield: {
      type: String,
      default: null,
    },
    scaledYield: {
      type: String,
      default: null,
    },
    basicYieldNum: {
      type: Number,
      default: null,
    },
    editScale: {
      type: Boolean,
      default: false,
    },
    value: {
      type: Number,
      required: true,
    },
  },
  setup(props, { emit }) {
    const menu = ref<boolean>(false);

    const scale = computed({
      get: () => props.value,
      set: (value) => {
        const newScaleNumber = parseFloat(`${value}`);
        emit("input", isNaN(newScaleNumber) ? 0 : newScaleNumber);
      },
    });

    const numerator = ref<number>(props.basicYieldNum != null ? parseFloat(props.basicYieldNum.toFixed(3)) : 1);
    const denominator = props.basicYieldNum != null ? parseFloat(props.basicYieldNum.toFixed(32)) : 1;
    const numberParsed = !!props.basicYieldNum;

    watch(() => numerator.value, () => {
      scale.value = parseFloat((numerator.value / denominator).toFixed(32));
    });
    const disableDecrement = computed(() => {
      return numerator.value <= 1;
    });


    return {
      menu,
      scale,
      numerator,
      disableDecrement,
      numberParsed,
    };
  },
});
</script>
