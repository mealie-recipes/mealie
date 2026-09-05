<template>
  <div class="text-subtitle-1 dense-markdown ingredient-item">
    <SafeMarkdown
      v-if="parsedIng.quantity"
      class="d-inline"
      :source="parsedIng.quantity"
    />
    <template v-if="parsedIng.unit">
      {{ parsedIng.unit }}
    </template>
    <template v-if="parsedIng.note && !parsedIng.name">
      <SafeMarkdown class="text-bold d-inline" :source="parsedIng.note" />
      <RecipeIngredientSubstitutions v-if="showSubstitutions" :ingredient="ingredient" />
    </template>
    <template v-else-if="parsedIng.recipeLink">
      <SafeMarkdown class="text-bold d-inline" :source="parsedIng.recipeLink" />
      <RecipeIngredientSubstitutions v-if="showSubstitutions" :ingredient="ingredient" />
      <SafeMarkdown v-if="parsedIng.note" class="note" :source="parsedIng.note" />
    </template>
    <template v-else>
      <SafeMarkdown
        v-if="parsedIng.name"
        class="text-bold d-inline"
        :source="parsedIng.name"
      />
      <!-- sits before the note, which takes a full flex row of its own -->
      <RecipeIngredientSubstitutions v-if="showSubstitutions" :ingredient="ingredient" />
      <SafeMarkdown
        v-if="parsedIng.note"
        class="note"
        :source="parsedIng.note"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import type { RecipeIngredient } from "~/lib/api/types/household";
import { useIngredientTextParser } from "~/composables/recipes";
import RecipeIngredientSubstitutions from "~/components/Domain/Recipe/RecipeIngredientSubstitutions.vue";

interface Props {
  ingredient: RecipeIngredient;
  scale?: number;
  // off by default: the shopping list and the add-to-list dialog reuse this row, and a menu
  // button is noise in both. the recipe renderer opts in
  showSubstitutions?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  scale: 1,
  showSubstitutions: false,
});
const route = useRoute();
const auth = useMealieAuth();
const groupSlug = computed(() => route.params.groupSlug || auth.user?.value?.groupSlug || "");
const { useParsedIngredientText } = useIngredientTextParser();

const parsedIng = computed(() => {
  return useParsedIngredientText(props.ingredient, props.scale, true, groupSlug.value.toString());
});
</script>

<style lang="scss">
.ingredient-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.25em;
  word-break: break-word;
  min-width: 0;

  .d-inline {
    & > p {
      display: inline;
      &:has(> sub) > sup {
        letter-spacing: -0.05rem;
      }
    }
    &:has(sub) {
      &:after {
        letter-spacing: -0.2rem;
      }
    }
    sup {
      & + span {
        letter-spacing: -0.05rem;
      }
      &:before {
        letter-spacing: 0rem;
      }
    }
  }

  .text-bold {
    font-weight: bold;
    white-space: normal;
    word-break: break-word;
  }
}

.note {
  flex-basis: 100%;
  width: 100%;
  display: block;
  line-height: 1.3em;
  font-size: 0.8em;
  opacity: 0.7;
  white-space: normal;
  word-break: break-word;
}
</style>
