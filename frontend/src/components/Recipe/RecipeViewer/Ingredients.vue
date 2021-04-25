<template>
  <div>
    <h2 class="mb-4">{{ $t("recipe.ingredients") }}</h2>
    <v-list-item
      dense
      v-for="(ingredient, index) in ingredients"
      :key="generateKey('ingredient', index)"
      @click="toggleChecked(index)"
    >
      <v-checkbox
        hide-details
        :value="checked[index]"
        class="pt-0 my-auto py-auto"
        color="secondary"
      >
      </v-checkbox>

      <v-list-item-content>
        <vue-markdown
          class="ma-0 pa-0 text-subtitle-1 dense-markdown"
          :source="ingredient"
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
      checked: [],
    };
  },
  mounted() {
    this.checked = this.ingredients.map(() => false);
    console.log(this.checked);
  },
  watch: {
    ingredients(val) {
      console.log(val);
    },
  },
  methods: {
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
    toggleChecked(index) {
      this.$set(this.checked, index, !this.checked[index]);
    },
  },
};
</script>

<style >
.dense-markdown p {
  margin: auto !important;
}
</style>