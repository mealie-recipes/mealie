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
            dense
            :value="value[key]"
            :label="labels[key].label"
            :suffix="labels[key].suffix"
            type="number"
            autocomplete="off"
            @input="updateValue(key, $event)"
          ></v-text-field>
        </div>
      </v-card-text>
      <v-list v-if="showViewer" dense class="mt-0 pt-0">
        <v-list-item v-for="(item, key, index) in labels" :key="index" style="min-height: 25px" dense>
          <v-list-item-content>
            <v-list-item-title class="pl-4 caption flex row">
              <div>{{ item.label }}</div>
              <div class="ml-auto mr-1">{{ value[key] }}</div>
              <div>{{ item.suffix }}</div>
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    value: {
      type: Object,
      required: true,
    },
    edit: {
      type: Boolean,
      default: true,
    },
  },
  setup(props, context) {
    const { i18n } = useContext();
    const labels = {
      calories: {
        label: i18n.t("recipe.calories"),
        suffix: i18n.t("recipe.calories-suffix"),
      },
      fatContent: {
        label: i18n.t("recipe.fat-content"),
        suffix: i18n.t("recipe.grams"),
      },
      fiberContent: {
        label: i18n.t("recipe.fiber-content"),
        suffix: i18n.t("recipe.grams"),
      },
      proteinContent: {
        label: i18n.t("recipe.protein-content"),
        suffix: i18n.t("recipe.grams"),
      },
      sodiumContent: {
        label: i18n.t("recipe.sodium-content"),
        suffix: i18n.t("recipe.milligrams"),
      },
      sugarContent: {
        label: i18n.t("recipe.sugar-content"),
        suffix: i18n.t("recipe.grams"),
      },
      carbohydrateContent: {
        label: i18n.t("recipe.carbohydrate-content"),
        suffix: i18n.t("recipe.grams"),
      },
    };
    const valueNotNull = computed(() => {
      for (const property in props.value) {
        const valueProperty = props.value[property];
        if (valueProperty && valueProperty !== "") return true;
      }
      return false;
    });

    const showViewer = computed(() => !props.edit && valueNotNull.value);

    function updateValue(key: number | string, event: Event) {
      context.emit("input", { ...props.value, [key]: event });
    }

    return {
      labels,
      valueNotNull,
      showViewer,
      updateValue
    }
  },
});
</script>

<style lang="scss" scoped></style>
