<template>
  <v-empty-state color="success" :icon="$globals.icons.progressCheck" :headline="$t('recipe.parser.ingredient-parser-headline')">
    <div class="d-flex ga-2 flex-column">
      <h3 class="my-0">
        {{ $t("recipe.parser.ingredient-parser-title") }}
      </h3>
      <p>{{ $t("recipe.parser.ingredient-parser-description") }}</p>
      <p>{{ $t("recipe.parser.ingredient-parser-final-review-description") }}</p>
      <h3 class="mb-0">
        {{ $t("recipe.parser.ingredient-parser-result-title") }}
      </h3>
      <div class="d-flex ga-2 flex-wrap">
        <v-chip v-if="autoParsed" size="large" color="success" :prepend-icon="$globals.icons.checkboxMarkedCircle">
          {{ $t("recipe.parser.ingredient-parser-result-success", autoParsed) }}
        </v-chip>
        <v-chip size="large" color="warning" :prepend-icon="$globals.icons.alert">
          {{ $t("recipe.parser.ingredient-parser-result-failed", toReview) }}
        </v-chip>
      </div>
    </div>
  </v-empty-state>
  <v-checkbox
    v-model="dontShowAgain"
    class="ml-3"
    hide-details
    density="compact"
    :label="$t('recipe.parser.dont-show-again')"
  />
</template>

<script setup lang="ts">
const dontShowAgain = defineModel<boolean>({ default: true });
defineProps<{
  autoParsed: number;
  toReview: number;
}>();
</script>
