<template>
  <div>
    <h2 class="mb-4">{{ $t("recipe.ingredients") }}</h2>
    <v-list-item
      dense
      v-for="(ingredient, index) in displayIngredients"
      :key="generateKey('ingredient', index)"
      @click="ingredient.checked = !ingredient.checked"
    >
      <v-checkbox
        hide-details
        v-model="ingredient.checked"
        class="pt-0 my-auto py-auto"
        color="secondary"
        :readonly="true"
      >
      </v-checkbox>

      <v-list-item-content>
        <vue-markdown
          class="ma-0 pa-0 text-subtitle-1 dense-markdown"
          :source="ingredient.text"
        >
        </vue-markdown>
      </v-list-item-content>
    </v-list-item>
  </div>
</template>

<script>
import VueMarkdown from "@adapttive/vue-markdown";
import utils from "@/utils";
export default {
  components: {
    VueMarkdown,
  },
  props: {
    ingredients: Array,
  },
  computed: {
    displayIngredients() {
      return this.ingredients.map(x => ({
        text: x,
        checked: false,
      }));
    },
  },
  methods: {
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
  },
};
</script>

<style >
.dense-markdown p {
  margin: auto !important;
}
</style>