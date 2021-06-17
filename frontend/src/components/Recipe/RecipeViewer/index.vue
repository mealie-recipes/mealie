<template>
  <div>
    <v-card-title class="headline">
      {{ recipe.name }}
    </v-card-title>
    <v-card-text>
      <vue-markdown :source="recipe.description"> </vue-markdown>
      <v-row dense disabled>
        <v-col>
          <v-btn
            v-if="recipe.recipeYield"
            dense
            small
            :hover="false"
            type="label"
            :ripple="false"
            elevation="0"
            color="secondary darken-1"
            class="rounded-sm static"
          >
            {{ recipe.recipeYield }}
          </v-btn>
        </v-col>
        <Rating :value="recipe.rating" :name="recipe.name" :slug="recipe.slug" :key="recipe.slug" />
      </v-row>
      <v-row>
        <v-col cols="12" sm="12" md="4" lg="4">
          <Ingredients :value="recipe.recipeIngredient" :edit="false" />
          <div v-if="medium">
            <v-card class="mt-2" v-if="recipe.recipeCategory.length > 0">
              <v-card-title class="py-2">
                {{ $t("recipe.categories") }}
              </v-card-title>
              <v-divider class="mx-2"></v-divider>
              <v-card-text>
                <RecipeChips :items="recipe.recipeCategory" />
              </v-card-text>
            </v-card>
            <v-card class="mt-2" v-if="recipe.tags.length > 0">
              <v-card-title class="py-2">
                {{ $t("tag.tags") }}
              </v-card-title>
              <v-divider class="mx-2"></v-divider>
              <v-card-text>
                <RecipeChips :items="recipe.tags" :isCategory="false" />
              </v-card-text>
            </v-card>

            <Nutrition v-if="recipe.settings.showNutrition" :value="recipe.nutrition" :edit="false" />
            <Assets v-if="recipe.settings.showAssets" :value="recipe.assets" :edit="false" :slug="recipe.slug" />
          </div>
        </v-col>
        <v-divider v-if="medium" class="my-divider" :vertical="true"></v-divider>

        <v-col cols="12" sm="12" md="8" lg="8">
          <Instructions :value="recipe.recipeInstructions" :edit="false" />
          <Notes :value="recipe.notes" :edit="false" />
        </v-col>
      </v-row>
      <div v-if="!medium">
        <RecipeChips :title="$t('recipe.categories')" :items="recipe.recipeCategory" />
        <RecipeChips :title="$t('tag.tags')" :items="recipe.tags" />
        <Nutrition v-if="recipe.settings.showNutrition" :value="recipe.nutrition" :edit="false" />
        <Assets v-if="recipe.settings.showAssets" :value="recipe.assets" :edit="false" :slug="recipe.slug" />
      </div>
      <v-row class="mt-2 mb-1">
        <v-col></v-col>
        <v-btn
          v-if="recipe.orgURL"
          dense
          small
          :hover="false"
          type="label"
          :ripple="false"
          elevation="0"
          :href="recipe.orgURL"
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
import { utils } from "@/utils";
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
    recipe: Object,
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
