<template>
  <v-container>
    <RecipeCardSection
      :icon="$globals.icons.primary"
      :title="$t('page.all-recipes')"
      :recipes="recipes"
      @delete="removeRecipe"
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
import { useLazyRecipes } from "~/composables/recipes";

export default defineComponent({
  components: { RecipeCardSection },
  setup() {
    const page = ref(1);
    const perPage = ref(30);
    const orderBy = "name";
    const orderDirection = "asc";

    const ready = ref(false);
    const loading = ref(false);

    const { recipes, fetchMore } = useLazyRecipes();

    onMounted(async () => {
      await fetchMore(page.value, perPage.value, orderBy, orderDirection);
      ready.value = true;
    });

    const infiniteScroll = useThrottleFn(() => {
      if (!ready.value) {
        return;
      }
      loading.value = true;
      page.value = page.value + 1;
      fetchMore(page.value, perPage.value, orderBy, orderDirection);
      loading.value = false;
    }, 500);

    function removeRecipe(slug: string) {
      for (let i = 0; i < recipes?.value?.length; i++) {
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
