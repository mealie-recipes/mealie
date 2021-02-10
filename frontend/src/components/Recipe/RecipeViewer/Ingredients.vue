<template>
  <div>
    <h2 class="mb-4">{{ $t("recipe.ingredients") }}</h2>
    <div
      v-for="(ingredient, index) in ingredients"
      :key="generateKey('ingredient', index)"
    >
      <v-checkbox
        hide-details
        class="ingredients"
        :label="ingredient"
        color="secondary"
      >
      </v-checkbox>
    </div>
  </div>
</template>

<script>
import utils from "@/utils";
export default {
  props: {
    ingredients: Array,
  },
  methods: {
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
  },
};
</script>

<style>
</style>