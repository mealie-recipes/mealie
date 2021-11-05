<template>
  <v-container>
    <RecipeCardSection
      :icon="$globals.icons.primary"
      :title="$t('page.all-recipes')"
      :recipes="recipes"
      @deleted="removeRecipe"
    ></RecipeCardSection>
    <v-card v-intersect="infiniteScroll"></v-card>
    <v-fade-transition>
      <AppLoader v-if="loading" :loading="loading" />
    </v-fade-transition>
  </v-container>
</template>
  
<script lang="ts">
import { defineComponent, onMounted, ref } from "@nuxtjs/composition-api";
import { useThrottleFn } from "@vueuse/core";
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { useLazyRecipes } from "~/composables/use-recipes";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const start = ref(0);
    const limit = ref(30);
    const increment = ref(30);
    const ready = ref(false);
    const loading = ref(false);

    const { recipes, fetchMore } = useLazyRecipes();

    onMounted(async () => {
      await fetchMore(start.value, limit.value);
      ready.value = true;
    });

    const infiniteScroll = useThrottleFn(() => {
      if (!ready.value) {
        return;
      }
      loading.value = true;
      start.value = limit.value + 1;
      limit.value = limit.value + increment.value;
      fetchMore(start.value, limit.value);
      loading.value = false;
    }, 500);

    function removeRecipe(slug: string) {
      // @ts-ignore
      for (let i = 0; i < recipes?.value?.length; i++) {
        // @ts-ignore
        if (recipes?.value[i].slug === slug) {
          recipes?.value.splice(i, 1);
          break;
        }
      }
    }

    return { recipes, infiniteScroll, loading, removeRecipe };
  },
  head() {
    return {
      title: this.$t("page.all-recipes") as string,
    };
  },
});
</script>
  