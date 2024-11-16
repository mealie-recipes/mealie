<template>
  <div>
    <div class="d-flex justify-end flex-wrap align-stretch">
      <RecipePageInfoCardImage v-if="landscape" :recipe="recipe" />
      <v-card
        :width="landscape ? null : '50%'"
        flat
        class="d-flex flex-column justify-center align-center"
      >
        <v-card-text>
          <v-card-title class="headline pa-0 flex-column align-center">
            {{ recipe.name }}
            <RecipeRating :key="recipe.slug" :value="recipe.rating" :recipe-id="recipe.id" :slug="recipe.slug" />
          </v-card-title>
          <v-divider class="my-2"></v-divider>
          <SafeMarkdown :source="recipe.description" />
          <v-divider></v-divider>
          <div v-if="isOwnGroup" class="d-flex justify-center mt-5">
            <RecipeLastMade
              v-model="recipe.lastMade"
              :recipe="recipe"
              class="d-flex justify-center flex-wrap"
              :class="true ? undefined : 'force-bottom'"
            />
          </div>
          <div class="d-flex justify-center mt-5">
            <RecipeTimeCard
              class="d-flex justify-center flex-wrap"
              :class="true ? undefined : 'force-bottom'"
              :prep-time="recipe.prepTime"
              :total-time="recipe.totalTime"
              :perform-time="recipe.performTime"
            />
          </div>
        </v-card-text>
      </v-card>
      <RecipePageInfoCardImage v-if="!landscape" :recipe="recipe" max-width="50%" />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import RecipeRating from "~/components/Domain/Recipe/RecipeRating.vue";
import RecipeLastMade from "~/components/Domain/Recipe/RecipeLastMade.vue";
import RecipeTimeCard from "~/components/Domain/Recipe/RecipeTimeCard.vue";
import RecipePageInfoCardImage from "~/components/Domain/Recipe/RecipePage/RecipePageParts/RecipePageInfoCardImage.vue";
export default defineComponent({
  components: {
    RecipeRating,
    RecipeLastMade,
    RecipeTimeCard,
    RecipePageInfoCardImage,
  },
  props: {
    recipe: {
      type: Object,
      required: true,
    },
    landscape: {
      type: Boolean,
      required: true,
    },
  },
  setup() {
    const { isOwnGroup } = useLoggedInState();

    return {
      isOwnGroup,
    };
  }
});
</script>
