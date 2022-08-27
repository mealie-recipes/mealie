<template>
  <div></div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { usePageState, usePageUser } from "~/composables/recipe-page/shared-state";
import { NoUndefinedField } from "~/types/api";
import { Recipe } from "~/types/api-types/recipe";
export default defineComponent({
  props: {
    recipe: {
      type: Object as () => NoUndefinedField<Recipe>,
      required: true,
    },
  },
  setup(props) {
    const { user } = usePageUser();
    const { imageKey } = usePageState(props.recipe.slug);

    return {
      user,
      imageKey,
    };
  },
});
</script>
