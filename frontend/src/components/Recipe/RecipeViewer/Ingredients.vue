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
        class=" pt-0 ingredients my-auto py-auto"
        color="secondary"
      >
      </v-checkbox>

      <v-list-item-content>
        <vue-markdown
          class="my-auto text-subtitle-1 mb-0"
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
  data() {
    return {
      displayIngredients: [],
    };
  },
  mounted() {
    this.displayIngredients = this.ingredients.map(x => ({
      text: x,
      checked: false,
    }));
  },
  methods: {
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
  },
};
</script>

<style>
p {
  margin-bottom: auto !important;
}

.my-card-text {
  overflow-wrap: break-word;
}
</style>