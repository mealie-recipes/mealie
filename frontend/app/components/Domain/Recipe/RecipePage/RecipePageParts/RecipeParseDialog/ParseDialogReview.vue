<template>
  <div class="d-flex flex-column ga-4">
    <ParseDialogChangeParser
      v-model="state.parser"
      :available-parsers="availableParsers"
      @update:model-value="$emit('changeParser', $event)"
      @parse="$emit('parse')"
    />
    <div>
      <v-card-title class="text-center pt-0 pb-8">
        {{ $t("recipe.parser.review-parsed-ingredients") }}
      </v-card-title>
      <v-card-text>
        <VueDraggable
          v-model="parsedIngs"
          handle=".handle"
          :delay="250"
          :delay-on-touch-only="true"
          v-bind="{
            animation: 200,
            group: 'recipe-ingredients',
            disabled: false,
            ghostClass: 'ghost',
          }"
          @start="drag = true"
          @end="drag = false"
        >
          <TransitionGroup type="transition">
            <v-lazy v-for="(ingredient, index) in parsedIngs" :key="index">
              <RecipeIngredientEditor
                v-model="ingredient.ingredient"
                enable-drag-handle
                enable-context-menu
                :delete-disabled="parsedIngs.length <= 1"
                @delete="parsedIngs.splice(index, 1)"
                @insert-above="insertNewIngredient(index)"
                @insert-below="insertNewIngredient(index + 1)"
              >
                <template #before-divider>
                  <p v-if="ingredient.input" class="py-0 my-0 text-caption">
                    {{ $t("recipe.original-text-with-value", { originalText: ingredient.input }) }}
                  </p>
                </template>
              </RecipeIngredientEditor>
            </v-lazy>
          </TransitionGroup>
        </VueDraggable>
      </v-card-text>
    </div>
  </div>
</template>

<script setup lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import type { MenuItem } from "~/components/global/BaseOverflowButton.vue";
import type { ParsedIngredient } from "~/lib/api/types/recipe";
import type { Parser } from "~/lib/api/user/recipes/recipe";

defineEmits<{
  parse: [];
  changeParser: [Parser];
}>();
const props = defineProps<{
  availableParsers: MenuItem[];
  parser: Parser;
}>();
const parsedIngs = defineModel<ParsedIngredient[]>({ required: true });

const state = reactive({
  parser: props.parser,
});

const drag = ref(false);

function insertNewIngredient(index: number) {
  const ing = {
    input: "",
    confidence: {},
    ingredient: {
      quantity: 0,
      referenceId: uuid4(),
    },
  } as ParsedIngredient;

  parsedIngs.value.splice(index, 0, ing);
}
</script>
