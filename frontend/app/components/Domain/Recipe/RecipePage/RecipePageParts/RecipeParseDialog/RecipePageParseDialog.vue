<template>
  <BaseDialog
    :model-value="modelValue"
    :title="$t('recipe.parse-ingredients')"
    :icon="$globals.icons.fileSign"
    disable-submit-on-enter
    @update:model-value="emit('update:modelValue', $event)"
  >
    <v-container fluid class="pa-2 ma-0" style="background-color: rgb(var(--v-theme-background));">
      <SwipeTransition direction="left">
        <!-- These wrapping divs appear to be load-bearing in making sure the transition renders correctly -->
        <div v-if="state.step === ParseStep.LOADING">
          <AppLoader class="my-6" />
        </div>
        <div v-else-if="state.step === ParseStep.INFO">
          <ParseDialogInfo v-model="dontShowInfoPage" />
        </div>
        <div
          v-else-if="state.step === ParseStep.PARSE && currentIng"
          :key="currentIng.ingredient.referenceId"
        >
          <ParseDialogParse :dialog-state="dialogState" />
        </div>
        <div v-else>
          <ParseDialogReview
            v-model="parsedIngs"
            :available-parsers="availableParsers"
            :parser="parser"
            @parse="parseIngredients"
            @change-parser="(newParser) => parser = newParser"
          />
        </div>
      </SwipeTransition>
    </v-container>
    <template v-if="state.step !== ParseStep.LOADING" #custom-card-action>
      <SpinTransition>
        <BaseButton
          v-if="state.step === ParseStep.INFO"
          color="info"
          icon-right
          :icon="$globals.icons.arrowRightBold"
          :text="$t('general.next')"
          @click="nextStep"
        />
        <BaseButton
          v-else-if="state.step === ParseStep.PARSE"
          :color="currentIngShouldDelete ? 'error' : 'info'"
          :icon="currentIngShouldDelete ? $globals.icons.delete : $globals.icons.arrowRightBold"
          :icon-right="!currentIngShouldDelete"
          :text="$t(currentIngShouldDelete ? 'recipe.parser.delete-item' : 'general.next')"
          @click="nextIngredient"
        />
        <BaseButton
          v-else-if="state.step === ParseStep.REVIEW"
          create
          :text="$t('general.save')"
          :icon="$globals.icons.save"
          :loading="state.saveLoading"
          @click="saveIngs"
        />
      </SpinTransition>
    </template>
  </BaseDialog>
</template>

<script setup lang="ts">
import { ParseStep, useParseIngredientsDialog } from "~/composables/recipes/use-parse-ingredients-dialog";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { RecipeIngredient } from "~/lib/api/types/recipe";

const props = defineProps<{
  modelValue: boolean;
  ingredients: NoUndefinedField<RecipeIngredient[]>;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void;
  (e: "save", value: NoUndefinedField<RecipeIngredient[]>): void;
}>();

const dialogState = useParseIngredientsDialog(props.ingredients, ings => emit("save", ings));

const {
  availableParsers,
  parser,
  dontShowInfoPage,
  parsedIngs,
  currentIng,
  currentIngShouldDelete,
  state,
  nextStep,
  saveIngs,
  nextIngredient,
  parseIngredients,
} = dialogState;

watch(() => props.modelValue, () => {
  if (!props.modelValue) {
    return;
  }

  parseIngredients();
});
</script>
