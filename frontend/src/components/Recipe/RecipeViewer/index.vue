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
        <Rating :value="rating" :name="name" :slug="slug" />
      </v-row>
      <v-row>
        <v-col cols="12" sm="12" md="4" lg="4">
          <Ingredients :value="ingredients" :edit="false" />
          <div v-if="medium">
            <v-card class="mt-2" v-if="categories.length > 0">
              <v-card-title class="py-2">
                {{ $t("recipe.categories") }}
              </v-card-title>
              <v-divider class="mx-2"></v-divider>
              <v-card-text>
                <RecipeChips :items="categories" />
              </v-card-text>
            </v-card>
            <v-card class="mt-2" v-if="tags.length > 0">
              <v-card-title class="py-2">
                {{ $t("tag.tags") }}
              </v-card-title>
              <v-divider class="mx-2"></v-divider>
              <v-card-text>
                <RecipeChips :items="tags" :isCategory="false" />
              </v-card-text>
            </v-card>

            <Nutrition :value="nutrition" :edit="false" />
            <Assets :value="assets" :edit="false" :slug="slug" />
          </div>
        </v-col>
        <v-divider v-if="medium" class="my-divider" :vertical="true"></v-divider>

        <v-col cols="12" sm="12" md="8" lg="8">
          <Instructions :value="instructions" :edit="false" />
          <Notes :value="notes" :edit="false" />
        </v-col>
      </v-row>
      <div v-if="!medium">
        <RecipeChips :title="$t('recipe.categories')" :items="categories" />
        <RecipeChips :title="$t('tag.tags')" :items="tags" />
        <Nutrition :value="nutrition" :edit="false" />
        <Assets :value="assets" :edit="false" :slug="slug" />
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
import Nutrition from "@/components/Recipe/Parts/Nutrition";
import VueMarkdown from "@adapttive/vue-markdown";
import utils from "@/utils";
import RecipeChips from "./RecipeChips";
import Rating from "@/components/Recipe/Parts/Rating";
import Notes from "@/components/Recipe/Parts/Notes";
import Ingredients from "@/components/Recipe/Parts/Ingredients";
import Instructions from "@/components/Recipe/Parts/Instructions.vue";
import Assets from "../Parts/Assets.vue";
export default {
  components: {
    VueMarkdown,
    RecipeChips,
    Notes,
    Ingredients,
    Nutrition,
    Instructions,
    Assets,
    Rating,
  },
  props: {
    name: String,
    slug: String,
    description: String,
    ingredients: Array,
    instructions: Array,
    categories: Array,
    tags: Array,
    notes: Array,
    rating: Number,
    yields: String,
    orgURL: String,
    nutrition: Object,
    assets: Array,
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
