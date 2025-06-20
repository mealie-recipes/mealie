<template>
  <v-img
    :key="imageKey"
    :max-width="maxWidth"
    min-height="50"
    cover
    width="100%"
    :height="hideImage ? undefined : imageHeight"
    :src="recipeImageUrl"
    class="d-print-none"
    @error="hideImage = true"
  />
</template>

<script lang="ts">
import { useStaticRoutes, useUserApi } from "~/composables/api";
import type { HouseholdSummary } from "~/lib/api/types/household";
import { usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import type { Recipe } from "~/lib/api/types/recipe";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";

export default defineNuxtComponent({
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
    maxWidth: {
      type: String,
      default: undefined,
    },
  },
  setup(props) {
    const { $vuetify } = useNuxtApp();
    const { recipeImage } = useStaticRoutes();
    const { imageKey } = usePageState(props.recipe.slug);
    const { user } = usePageUser();

    const recipeHousehold = ref<HouseholdSummary>();
    if (user) {
      const userApi = useUserApi();
      userApi.households.getOne(props.recipe.householdId).then(({ data }) => {
        recipeHousehold.value = data || undefined;
      });
    }

    const hideImage = ref(false);
    const imageHeight = computed(() => {
      return $vuetify.display.xs.value ? "200" : "400";
    });

    const recipeImageUrl = computed(() => {
      return recipeImage(props.recipe.id, props.recipe.image, imageKey.value);
    });

    watch(
      () => recipeImageUrl.value,
      () => {
        hideImage.value = false;
      },
    );

    return {
      recipeImageUrl,
      imageKey,
      hideImage,
      imageHeight,
    };
  },
});
</script>
