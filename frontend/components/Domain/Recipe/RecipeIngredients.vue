<template>
  <div v-if="value && value.length > 0">
    <div v-if="!isCookMode" class="d-flex justify-start" >
      <h2 class="mb-2 mt-1">{{ $t("recipe.ingredients") }}</h2>
      <AppButtonCopy btn-class="ml-auto" :copy-text="ingredientCopyText" />
    </div>
    <div>
      <div v-for="(ingredient, index) in value" :key="'ingredient' + index">
        <template v-if="!isCookMode">
          <h3 v-if="showTitleEditor[index]" class="mt-2">{{ ingredient.title }}</h3>
          <v-divider v-if="showTitleEditor[index]"></v-divider>
        </template>
        <v-list-item dense @click.stop="toggleChecked(index)">
          <v-checkbox hide-details :value="checked[index]" class="pt-0 my-auto py-auto" color="secondary" />
          <v-list-item-content :key="ingredient.quantity">
            <RecipeIngredientListItem :ingredient="ingredient" :disable-amount="disableAmount" :scale="scale" />
          </v-list-item-content>
        </v-list-item>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from "@nuxtjs/composition-api";
import RecipeIngredientListItem from "./RecipeIngredientListItem.vue";
import { parseIngredientText } from "~/composables/recipes";
import { RecipeIngredient } from "~/lib/api/types/recipe";

export default defineComponent({
  components: { RecipeIngredientListItem },
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
    isCookMode: {
      type: Boolean,
      default: false,
    }
  },
  setup(props) {
    function validateTitle(title?: string) {
      return !(title === undefined || title === "" || title === null);
    }

    const state = reactive({
      checked: props.value.map(() => false),
      showTitleEditor: computed(() => props.value.map((x) => validateTitle(x.title))),
    });

    const ingredientCopyText = computed(() => {
      const components: string[] = [];
      props.value.forEach((ingredient) => {
        if (ingredient.title) {
          if (components.length) {
            components.push("");
          }

          components.push(`[${ingredient.title}]`);
        }

        components.push(parseIngredientText(ingredient, props.disableAmount, props.scale, false));
      });

      return components.join("\n");
    });

    function toggleChecked(index: number) {
      // TODO Find a better way to do this - $set is not available, and
      // direct array modifications are not propagated for some reason
      state.checked.splice(index, 1, !state.checked[index]);
    }

    return {
      ...toRefs(state),
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
