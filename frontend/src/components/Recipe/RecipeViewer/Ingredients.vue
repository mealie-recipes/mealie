<template>
  <div>
    <h2 class="mb-4">{{ $t("recipe.ingredients") }}</h2>
    <div
      v-for="(ingredient, index) in ingredients"
      :key="generateKey('ingredient', index)"
    >
      <v-card flat>
        <v-card-text class="text-subtitle-1">
          <v-row class="flex row ">
            <v-checkbox
              hide-details
              class=" pt-0 ingredients my-auto py-auto"
              color="secondary"
            >
            </v-checkbox>
            <vue-markdown class="my-auto" :source="ingredient"> </vue-markdown>
          </v-row>
        </v-card-text>
      </v-card>
    </div>
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
</style>