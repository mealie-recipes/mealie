<template>
  <v-container>
    <RecipeCardSection
      :icon="$globals.icons.tags"
      :title="category.name"
      :recipes="category.recipes"
      @sort="assignSorted"
    ></RecipeCardSection>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent, useAsync, useRoute } from "@nuxtjs/composition-api";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useApiSingleton } from "~/composables/use-api";
import { Recipe } from "~/types/api-types/recipe";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const api = useApiSingleton();
    const route = useRoute();
    const slug = route.value.params.slug;

    const category = useAsync(async () => {
      const { data } = await api.categories.getOne(slug);
      return data;
    }, slug);
    return { category };
  },
  methods: {
    assignSorted(val: Array<Recipe>) {
      if (this.category) {
        this.category.recipes = val;
      }
    },
  },
});
</script>
    
<style scoped>
</style>