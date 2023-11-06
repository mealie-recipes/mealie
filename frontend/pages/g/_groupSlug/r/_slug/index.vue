<template>
  <div>
    <RecipePage v-if="recipe" :recipe="recipe" />
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useAsync, useContext, useMeta, useRoute, useRouter } from "@nuxtjs/composition-api";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import RecipePage from "~/components/Domain/Recipe/RecipePage/RecipePage.vue";
import { usePublicExploreApi } from "~/composables/api/api-client";
import { useRecipe } from "~/composables/recipes";
import { Recipe } from "~/lib/api/types/recipe";

export default defineComponent({
  components: { RecipePage },
  setup() {
    const  { $auth } = useContext();
    const { isOwnGroup } = useLoggedInState();
    const route = useRoute();
    const router = useRouter();
    const slug = route.value.params.slug;

    const { title } = useMeta();

    let recipe = ref<Recipe | null>(null);
    if (isOwnGroup.value) {
      const { recipe: data } = useRecipe(slug);
      recipe = data;
    } else {
      const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "")
      const api = usePublicExploreApi(groupSlug.value);
      recipe = useAsync(async () => {
        const { data, error } = await api.explore.recipes.getOne(slug);

        if (error) {
          console.error("error loading recipe -> ", error);
          router.push(`/g/${groupSlug.value}`);
        }

        return data;
      })
    }

    title.value = recipe.value?.name || "";

    return {
      recipe,
    };
  },
  head() {
    if (this.recipe) {
      return {
        title: this.recipe.name
      }
    }
  }
});
</script>
