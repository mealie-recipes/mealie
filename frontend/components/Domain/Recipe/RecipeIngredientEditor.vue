<template>
  <div>
    <v-text-field
      v-if="value.title || showTitle"
      v-model="value.title"
      dense
      hide-details
      class="mx-1 mb-4"
      placeholder="Section Title"
      style="max-width: 500px"
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
          placeholder="Quantity"
        >
          <v-icon slot="prepend" class="mr-n1" color="error" @click="$emit('delete')">
            {{ $globals.icons.delete }}
          </v-icon>
        </v-text-field>
      </v-col>
      <v-col v-if="!disableAmount && units" sm="12" md="3" cols="12">
        <v-select
          v-model="value.unit"
          hide-details
          dense
          solo
          return-object
          :items="units"
          item-text="name"
          class="mx-1"
          placeholder="Choose Unit"
        >
        </v-select>
      </v-col>
      <v-col v-if="!disableAmount && foods" m="12" md="3" cols="12" class="">
        <v-select
          v-model="value.food"
          hide-details
          dense
          solo
          return-object
          :items="foods"
          item-text="name"
          class="mx-1 py-0"
          placeholder="Choose Food"
        >
        </v-select>
      </v-col>
      <v-col sm="12" md="" cols="12">
        <v-text-field v-model="value.note" hide-details dense solo class="mx-1" placeholder="Notes">
          <v-icon v-if="disableAmount" slot="prepend" class="mr-n1" color="error" @click="$emit('delete')">
            {{ $globals.icons.delete }}
          </v-icon>
          <template slot="append">
            <v-tooltip top nudge-right="10">
              <template #activator="{ on, attrs }">
                <v-btn icon small class="mt-n1" v-bind="attrs" v-on="on" @click="toggleTitle()">
                  <v-icon>{{ showTitle || value.title ? $globals.icons.minus : $globals.icons.createAlt }}</v-icon>
                </v-btn>
              </template>
              <span>{{ showTitle ? $t("recipe.remove-section") : $t("recipe.insert-section") }}</span>
            </v-tooltip>
          </template>
          <template slot="append-outer">
            <v-icon class="handle">{{ $globals.icons.arrowUpDown }}</v-icon>
          </template>
        </v-text-field>
      </v-col>
    </v-row>
    <v-divider v-if="!$vuetify.breakpoint.mdAndUp" class="my-4"></v-divider>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from "@nuxtjs/composition-api";
import { useFoods } from "~/composables/use-recipe-foods";
import { useUnits } from "~/composables/use-recipe-units";

export default defineComponent({
  props: {
    value: {
      type: Object,
      required: true,
    },
    disableAmount: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const { value } = props;

    const { foods } = useFoods();
    const { units } = useUnits();

    const state = reactive({
      showTitle: false,
    });

    function toggleTitle() {
      if (value.title) {
        state.showTitle = false;
        value.title = "";
      } else {
        state.showTitle = true;
        value.title = "Section Title";
      }
    }

    return { foods, units, ...toRefs(state), toggleTitle };
  },
});
</script>

