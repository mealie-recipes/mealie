<template>
  <v-container>
    <RecipeCardSection
      :icon="$globals.icons.primary"
      :title="$t('page.all-recipes')"
      :recipes="recipes"
      @sort="assignSorted"
    ></RecipeCardSection>
  </v-container>
</template>
  
  <script lang="ts">
import { defineComponent, onMounted, ref } from "@nuxtjs/composition-api";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useApiSingleton } from "~/composables/use-api";
import { Recipe } from "~/types/api-types/admin";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const api = useApiSingleton();

    const recipes = ref<Recipe[] | null>([]);
    onMounted(async () => {
      const { data } = await api.recipes.getAll();
      recipes.value = data;
    });

    return { api, recipes };
  },
  methods: {
    assignSorted(val: Array<Recipe>) {
      this.recipes = val;
    },
  },
});
</script>
  