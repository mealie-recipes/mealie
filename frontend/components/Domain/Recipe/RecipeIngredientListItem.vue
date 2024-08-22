<template>
  <div class="ma-0 pa-0 text-subtitle-1 dense-markdown ingredient-item">
    <SafeMarkdown v-if="parsedIng.quantity" class="d-inline" :source="parsedIng.quantity" />
    <template v-if="parsedIng.unit">{{ parsedIng.unit }} </template>
    <SafeMarkdown v-if="parsedIng.note && !parsedIng.name" class="text-bold d-inline" :source="parsedIng.note" />
    <template v-else>
      <SafeMarkdown v-if="parsedIng.name" class="text-bold d-inline" :source="parsedIng.name" />
      <SafeMarkdown v-if="parsedIng.note" class="note" :source="parsedIng.note" />
    </template>
  </div>
</template>
<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import { RecipeIngredient } from "~/lib/api/types/household";
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
    const parsedIng = computed(() => {
      return useParsedIngredientText(props.ingredient, props.disableAmount, props.scale);
    });

    return {
      parsedIng,
    };
  },
});
</script>
<style lang="scss">
.ingredient-item {
  .d-inline {
    & > p {
      display: inline;
      &:has(>sub)>sup {
        letter-spacing: -0.05rem;
      }
    }
    &:has(sub) {
      &:after {
        letter-spacing: -0.2rem;
      }
    }
    sup {
      &+span{
        letter-spacing: -0.05rem;
      }
      &:before {
        letter-spacing: 0rem;
      }
    }
  }

  .text-bold {
    font-weight: bold;
  }
}

.note {
  line-height: 1.25em;
  font-size: 0.8em;
  opacity: 0.7;
}
</style>
