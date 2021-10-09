<template>
  <v-container v-if="recipe">
    <v-container>
      <BaseCardSectionTitle title="Ingredients Processor"> </BaseCardSectionTitle>
      <v-card-actions class="justify-end">
        <BaseButton color="info">
          <template #icon> {{ $globals.icons.foods }}</template>
          Parse All
        </BaseButton>
        <BaseButton save> Save All </BaseButton>
      </v-card-actions>

      </v-card>
      <v-expansion-panels v-model="panels" multiple>
        <v-expansion-panel v-for="(ing, index) in ingredients" :key="index">
          <v-expansion-panel-header class="my-0 py-0">
            {{ recipe.recipeIngredient[index].note }}
          </v-expansion-panel-header>
          <v-expansion-panel-content class="pb-0 mb-0">
            <RecipeIngredientEditor v-model="ingredients[index]" />
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-container>
  </v-container>
</template>
  
<script lang="ts">
import { defineComponent, reactive, ref, toRefs, useRoute, watch } from "@nuxtjs/composition-api";
import RecipeIngredientEditor from "~/components/Domain/Recipe/RecipeIngredientEditor.vue";
import { useApiSingleton } from "~/composables/use-api";
import { useRecipeContext } from "~/composables/use-recipe-context";
export default defineComponent({
  components: {
    RecipeIngredientEditor,
  },
  setup() {
    const state = reactive({
      panels: null,
    });
    const route = useRoute();
    const slug = route.value.params.slug;
    const api = useApiSingleton();

    const { getBySlug, loading } = useRecipeContext();

    const recipe = getBySlug(slug);

    const ingredients = ref<any[]>([]);

    watch(recipe, () => {
      const copy = recipe?.value?.recipeIngredient || [];
      ingredients.value = [...copy];
    });

    return {
      ...toRefs(state),
      api,
      recipe,
      loading,
      ingredients,
    };
  },
  head() {
    return {
      title: "Parser",
    };
  },
});
</script>
  
<style scoped>
</style>