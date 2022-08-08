<template>
  <div>
    <div class="text-center d-flex align-center">
      <div>
        <v-menu v-model="menu" :disabled="!editScale" offset-y top nudge-top="6" :close-on-content-click="false">
          <template #activator="{ on, attrs }">
            <v-card class="pa-1 px-2" dark color="secondary darken-1" small v-bind="attrs" v-on="on">
              <span v-if="recipeYield"> {{ scaledYield }} </span>
              <span v-if="!recipeYield"> x {{ scale }} </span>
            </v-card>
          </template>
          <v-card min-width="300px">
            <v-card-title class="mb-0">
              {{ $t("recipe.edit-scale") }}
            </v-card-title>
            <v-card-text class="mt-n5">
              <div class="mt-4 d-flex align-center">
                <v-text-field v-model.number="scale" type="number" :min="0" :label="$t('recipe.edit-scale')" />
                <v-tooltip right color="secondary darken-1">
                  <template #activator="{ on, attrs }">
                    <v-btn v-bind="attrs" icon class="mx-1" small v-on="on" @click="scale = 1">
                      <v-icon>
                        {{ $globals.icons.undo }}
                      </v-icon>
                    </v-btn>
                  </template>
                  <span> {{ $t("recipe.reset-scale") }} </span>
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
            text: $t('recipe.decrease-scale-label'),
            event: 'decrement',
          },
          {
            icon: $globals.icons.createAlt,
            text: $t('recipe.increase-scale-label'),
            event: 'increment',
          },
        ]"
        @decrement="scale > 1 ? scale-- : null"
        @increment="scale++"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, computed } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    recipeYield: {
      type: String,
      default: null,
    },
    basicYield: {
      type: String,
      default: null,
    },
    scaledYield: {
      type: String,
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
    const state = reactive({
      tempScale: 1,
      menu: false,
    });

    const scale = computed({
      get: () => props.value,
      set: (value) => {
        const newScaleNumber = parseFloat(`${value}`);
        emit("input", isNaN(newScaleNumber) ? 0 : newScaleNumber);
      },
    });

    return {
      scale,
      ...toRefs(state),
    };
  },
});
</script>
