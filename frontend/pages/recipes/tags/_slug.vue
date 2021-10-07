<template>
  <v-container>
    <RecipeCardSection
      v-if="tag"
      :icon="$globals.icons.tags"
      :title="tag.name"
      :recipes="tag.recipes"
      @sort="assignSorted"
    ></RecipeCardSection>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent, useAsync, useRoute } from "@nuxtjs/composition-api";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useApiSingleton } from "~/composables/use-api";
import { Recipe } from "~/types/api-types/admin";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const api = useApiSingleton();
    const route = useRoute();
    const slug = route.value.params.slug;

    const tag = useAsync(async () => {
      const { data } = await api.tags.getOne(slug);
      return data;
    }, slug);
    return { tag };
  },
  head() {
    return {
      title: this.$t("sidebar.tags") as string,
    };
  },
  methods: {
    assignSorted(val: Array<Recipe>) {
      if (this.tag) {
        // @ts-ignore
        this.tag.recipes = val;
      }
    },
  },
});
</script>
    
<style scoped>
</style>