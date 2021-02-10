<template>
  <div>
    <v-card-title class="headline">
      {{ name }}
    </v-card-title>
    <v-card-text>
      <vue-markdown :source="description"> </vue-markdown>
      <v-row dense disabled>
        <v-col>
          <v-btn
            v-if="yields"
            dense
            small
            :hover="false"
            type="label"
            :ripple="false"
            elevation="0"
            color="secondary darken-1"
            class="rounded-sm static"
          >
            {{ yields }}
          </v-btn>
        </v-col>
        <v-rating
          class="mr-2 align-end static"
          color="secondary darken-1"
          background-color="secondary lighten-3"
          length="5"
          :value="rating"
        ></v-rating>
      </v-row>
      <v-row>
        <v-col cols="12" sm="12" md="4" lg="4">
          <Ingredients :ingredients="ingredients" />
          <div v-if="medium">
            <RecipeChips :title="$t('recipe.categories')" :items="categories" />
            <RecipeChips :title="$t('recipe.tags')" :items="tags" />
            <Notes :notes="notes" />
          </div>
        </v-col>
        <v-divider
          v-if="medium"
          class="my-divider"
          :vertical="true"
        ></v-divider>

        <v-col cols="12" sm="12" md="8" lg="8">
          <Steps :steps="instructions" />
        </v-col>
      </v-row>
      <div v-if="!medium">
        <RecipeChips :title="$t('recipe.categories')" :items="categories" />
        <RecipeChips :title="$t('recipe.tags')" :items="tags" />
        <Notes :notes="notes" />
      </div>
      <v-row class="mt-2 mb-1">
        <v-col></v-col>
        <v-btn
          v-if="orgURL"
          dense
          small
          :hover="false"
          type="label"
          :ripple="false"
          elevation="0"
          :href="orgURL"
          color="secondary darken-1"
          target="_blank"
          class="rounded-sm mr-4"
        >
          {{ $t("recipe.original-url") }}
        </v-btn>
      </v-row>
    </v-card-text>
  </div>
</template>

<script>
import VueMarkdown from "@adapttive/vue-markdown";
import utils from "@/utils";
import RecipeChips from "./RecipeChips";
import Steps from "./Steps";
import Notes from "./Notes";
import Ingredients from "./Ingredients";
export default {
  components: {
    VueMarkdown,
    RecipeChips,
    Steps,
    Notes,
    Ingredients,
  },
  props: {
    name: String,
    description: String,
    ingredients: Array,
    instructions: Array,
    categories: Array,
    tags: Array,
    notes: Array,
    rating: Number,
    yields: String,
    orgURL: String,
  },
  data() {
    return {
      disabledSteps: [],
    };
  },
  computed: {
    medium() {
      return this.$vuetify.breakpoint.mdAndUp;
    },
  },
  methods: {
    generateKey(item, index) {
      return utils.generateUniqueKey(item, index);
    },
  },
};
</script>

<style>
.static {
  pointer-events: none;
}
.my-divider {
  margin: 0 -1px;
}
</style>