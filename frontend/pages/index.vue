<template>
  <v-container>
    <RecipeCardSection
      :icon="$globals.icons.primary"
      :title="$t('general.recent')"
      :recipes="recentRecipes"
    ></RecipeCardSection>
  </v-container>
</template>

<script lang="ts" setup>
import RecipeCardSection from "~/components/Domain/Recipe/RecipeCardSection.vue";
import { recentRecipes } from "~/composables/use-recipes";
</script>
