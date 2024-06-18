<template>
  <div v-if="valueNotNull || edit">
    <v-card class="mt-2">
      <v-card-title class="pt-2 pb-0">
        {{ $t("recipe.nutrition") }}
      </v-card-title>
      <v-divider class="mx-2 my-1"></v-divider>
      <v-card-text v-if="edit">
        <div v-for="(item, key, index) in value" :key="index">
          <v-text-field
dense :value="value[key]" :label="labels[key].label" :suffix="labels[key].suffix" type="number"
            autocomplete="off" @input="updateValue(key, $event)"></v-text-field>
        </div>
      </v-card-text>
      <v-list v-if="showViewer" dense class="mt-0 pt-0">
        <v-list-item v-for="(item, key, index) in renderedList" :key="index" style="min-height: 25px" dense>
          <v-list-item-content>
            <v-list-item-title class="pl-4 caption flex row">
              <div>{{ item.label }}</div>
              <div class="ml-auto mr-1">{{ item.value }}</div>
              <div>{{ item.suffix }}</div>
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import { useNutritionLabels } from "~/composables/recipes";
import { Nutrition } from "~/lib/api/types/recipe";
import { NutritionLabelType } from "~/composables/recipes/use-recipe-nutrition";
export default defineComponent({
  props: {
    value: {
      type: Object as () => Nutrition,
      required: true,
    },
    edit: {
      type: Boolean,
      default: true,
    },
  },
  setup(props, context) {
    const { labels } = useNutritionLabels();
    const valueNotNull = computed(() => {
      let key: keyof Nutrition;
      for (key in props.value) {
        if (props.value[key] !== null) {
          return true;
        }
      }
      return false;
    });

    const showViewer = computed(() => !props.edit && valueNotNull.value);

    function updateValue(key: number | string, event: Event) {
      context.emit("input", { ...props.value, [key]: event });
    }

    // Build a new list that only contains nutritional information that has a value
    const renderedList = computed(() => {
      return Object.entries(labels).reduce((item: NutritionLabelType, [key, label]) => {
        if (props.value[key]?.trim()) {
          item[key] = {
            ...label,
            value: props.value[key],
          };
        }
        return item;
      }, {});
    });

    return {
      labels,
      valueNotNull,
      showViewer,
      updateValue,
      renderedList,
    };
  },
});
</script>

<style lang="scss" scoped></style>
