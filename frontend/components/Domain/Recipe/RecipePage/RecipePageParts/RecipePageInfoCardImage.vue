<template>
  <v-img
    :key="imageKey"
    :max-width="maxWidth"
    min-height="50"
    :height="hideImage ? undefined : imageHeight"
    :src="recipeImageUrl"
    class="d-print-none"
    @error="hideImage = true"
  />
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext, watch } from "@nuxtjs/composition-api";
import { useStaticRoutes, useUserApi  } from "~/composables/api";
import { HouseholdSummary } from "~/lib/api/types/household";
import { usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import { Recipe } from "~/lib/api/types/recipe";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
export default defineComponent({
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
    const { $vuetify } = useContext();
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
      return $vuetify.breakpoint.xs ? "200" : "400";
    });

    const recipeImageUrl = computed(() => {
      return recipeImage(props.recipe.id, props.recipe.image, imageKey.value);
    });

    watch(
      () => recipeImageUrl.value,
      () => {
        hideImage.value = false;
      }
    );

    return {
      recipeImageUrl,
      imageKey,
      hideImage,
      imageHeight,
    };
  }
});
</script>
