<template>
  <div class="ma-0 pa-0 text-subtitle-1 dense-markdown ingredient-item">
    <span class="quantity">
      <SafeMarkdown v-if="quantity" class="d-inline" :source="quantity" />
      <template v-if="unit">{{ unit }} </template>
    </span>
    <SafeMarkdown v-if="note && !name" class="d-inline" :source="note" />
    <template v-else>
      <SafeMarkdown v-if="name" class="d-inline" :source="name" />
      <SafeMarkdown v-if="note" class="note" :source="note" />
    </template>
  </div>
</template>
<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { RecipeIngredient } from "~/lib/api/types/group";
import { useParsedIngredientText } from "~/composables/recipes";

export default defineComponent({
  props: {
    ingredient: {
      type: Object as () => RecipeIngredient,
      required: true,
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
    const parsed = useParsedIngredientText(props.ingredient, props.disableAmount, props.scale);
    return {
      ...parsed,
    };
  },
});
</script>
<style>
.quantity {
  color: var(--v-accent-darken1);
}

.ingredient-item {
  .d-inline {
    & > p {
      display: inline;
    }
  }
}

.dark {
  .quantity {
    color: var(--v-accent-lighten3);
  }
}

.note {
  line-height: 0.8em;
  font-size: 0.8em;
  opacity: 0.7;
}
</style>
