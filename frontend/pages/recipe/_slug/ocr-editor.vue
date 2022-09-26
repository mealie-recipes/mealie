<template>
  <div>
    <RecipeOcrEditorPage v-if="recipe" :recipe="recipe" />
  </div>
</template>

<script lang="ts">
import { defineComponent, useRoute } from "@nuxtjs/composition-api";
import RecipeOcrEditorPage from "~/components/Domain/Recipe/RecipeOcrEditorPage/RecipeOcrEditorPage.vue";
import { useRecipe } from "~/composables/recipes";

export default defineComponent({
  components: { RecipeOcrEditorPage },
  setup() {
    const route = useRoute();
    const slug = route.value.params.slug;

    const { recipe, loading } = useRecipe(slug);

    return {
      recipe,
      loading,
    };
  },
});
</script>

<style lang="css">
.ghost {
  opacity: 0.5;
}

body {
  background: #eee;
}

canvas {
  background: white;
  box-shadow: 0px 2px 3px rgba(0, 0, 0, 0.2);
  width: 100%;
  image-rendering: optimizeQuality;
}

.box {
  position: absolute;
  border: 2px #90ee90 solid;
  background-color: #90ee90;

  z-index: 3;
}
</style>
