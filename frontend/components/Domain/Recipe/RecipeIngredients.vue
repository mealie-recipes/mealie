<template>
  <div v-if="value && value.length > 0">
    <div class="d-flex justify-start">
      <h2 class="mb-2 mt-1">{{ $t("recipe.ingredients") }}</h2>
      <AppButtonCopy btn-class="ml-auto" :copy-text="ingredientCopyText" />
    </div>
    <div>
      <div v-for="(ingredient, index) in value" :key="'ingredient' + index">
        <h3 v-if="showTitleEditor[index]" class="mt-2">{{ ingredient.title }}</h3>
        <v-divider v-if="showTitleEditor[index]"></v-divider>
        <v-list-item dense @click="toggleChecked(index)">
          <v-checkbox hide-details :value="checked[index]" class="pt-0 my-auto py-auto" color="secondary"> </v-checkbox>
          <v-list-item-content>
            <VueMarkdown
              class="ma-0 pa-0 text-subtitle-1 dense-markdown"
              :source="parseIngredientText(ingredient, disableAmount, scale)"
            >
            </VueMarkdown>
          </v-list-item-content>
        </v-list-item>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from "@nuxtjs/composition-api";
// @ts-ignore
import VueMarkdown from "@adapttive/vue-markdown";
import { parseIngredientText } from "~/composables/recipes";
import { RecipeIngredient } from "~/types/api-types/recipe";

export default defineComponent({
  components: {
    VueMarkdown,
  },
  props: {
    value: {
      type: Array as () => RecipeIngredient[],
      default: () => [],
    },
    disableAmount: {
      type: Boolean,
      default: false,
    },
    scale: {
      type: Number,
      default: 1,
    },
  },
  setup(props) {
    function validateTitle(title?: string) {
      return !(title === undefined || title === "");
    }

    const state = reactive({
      checked: props.value.map(() => false),
      showTitleEditor: computed(() => props.value.map((x) => validateTitle(x.title))),
    });

    const ingredientCopyText = computed(() => {
      return props.value
        .map((ingredient) => {
          return `- [ ] ${parseIngredientText(ingredient, props.disableAmount, props.scale)}`;
        })
        .join("\n");
    });

    function toggleChecked(index: number) {
      // TODO Find a better way to do this - $set is not available, and
      // direct array modifications are not propagated for some reason
      state.checked.splice(index, 1, !state.checked[index]);
    }

    return {
      ...toRefs(state),
      parseIngredientText,
      ingredientCopyText,
      toggleChecked,
    };
  },
});
</script>

<style>
.dense-markdown p {
  margin: auto !important;
}
</style>
