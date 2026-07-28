<template>
  <SpinTransition>
    <v-empty-state color="success" :icon="$globals.icons.progressCheck" :headline="$t('recipe.parser.ingredient-parser-headline')">
      <div class="d-flex ga-2 flex-column">
        <h3 class="my-0">
          {{ $t("recipe.parser.ingredient-parser-title") }}
        </h3>
        <p>{{ $t("recipe.parser.ingredient-parser-description") }}</p>
        <p>{{ $t("recipe.parser.ingredient-parser-final-review-description") }}</p>
      </div>
    </v-empty-state>
  </SpinTransition>
  <v-checkbox
    v-model="dontShowAgain"
    hide-details
    density="compact"
    :label="$t('recipe.parser.dont-show-again')"
  />
</template>

<script setup lang="ts">
const dontShowAgain = defineModel<boolean>({ default: true });
</script>
