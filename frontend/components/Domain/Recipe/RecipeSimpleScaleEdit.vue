<template>
    <div class="text-center d-flex align-center ml-4" style="height: 24px;font-size: 12px" >
        <v-menu
            v-model="menu" offset-y top
            nudge-top="6"
            :disabled="!editScale"
            :close-on-content-click="false"
        >
            <template #activator="{ on, attrs }">
            <v-card class="pa-1 px-2" dark color="secondary darken-1" x-small v-bind="attrs" v-on="on">
                <span> x{{ scale }} </span>
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
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, computed } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    editScale: {
      type: Boolean,
      default: false,
    },
    value: {
      type: Number,
      required: true,
    }
  },
  setup(props, { emit }) {
    const state = reactive({
      tempScale: 1,
      menu: false,
    });

    const scale = computed({
      get: () => props.value,
      set: (value) => {
        const newScaleNumber = parseFloat(`${value.toString()}`);
        emit("input", isNaN(newScaleNumber) ? 0 : newScaleNumber);
      },
    });

    return {
      scale,
      ...toRefs(state),
    };
  }
});
</script>
