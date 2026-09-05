<template>
  <v-menu
    v-if="hasSubstitutions"
    location="bottom start"
    max-width="360"
  >
    <template #activator="{ props: menuProps }">
      <!-- click, not hover alone: this is read in a kitchen, on a phone, where nothing hovers -->
      <v-btn
        v-bind="menuProps"
        icon
        variant="plain"
        :aria-label="$t('recipe.substitutions')"
        @click.stop
      >
        <v-icon>
          {{ $globals.icons.swapHorizontal }}
        </v-icon>
      </v-btn>
    </template>
    <v-card class="ingredient-substitutions">
      <v-card-text class="py-2 px-3 text-body-2">
        <div
          v-for="section, sectionIndex in sections"
          :key="section.key"
          :class="[section.dimmed ? 'food-substitutions' : '', sectionIndex ? 'mt-5' : '']"
        >
          <div class="text-caption font-weight-medium substitution-header">
            {{ section.title }}
          </div>
          <div
            v-for="substitution, i in section.items"
            :key="i"
            class="substitution"
          >
            <template v-if="substitution.substituteFood">
              <span class="substitution-primary">{{ substitution.substituteFood.name }}</span>
              <SafeMarkdown v-if="substitution.note" class="substitution-note" :source="substitution.note" />
            </template>
            <!-- with no food the note is the substitution itself, so it reads like one, the way
                 an ingredient with a note and no food renders bold rather than dimmed -->
            <SafeMarkdown v-else-if="substitution.note" class="substitution-primary" :source="substitution.note" />
          </div>
        </div>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script setup lang="ts">
import { useIngredientSubstitutions } from "~/composables/recipes";
import type { IngredientFoodSubstitution, RecipeIngredient } from "~/lib/api/types/recipe";

interface Props {
  ingredient: RecipeIngredient;
}

const props = defineProps<Props>();

const i18n = useI18n();
const { recipeSubstitutions, foodSubstitutions, hasSubstitutions } = useIngredientSubstitutions(() => props.ingredient);

interface SubstitutionSection {
  key: string;
  title: string;
  items: IngredientFoodSubstitution[];
  dimmed: boolean;
}

// what this recipe says comes first and at full strength; what the food suggests everywhere
// sits behind it, and says so, which is what makes the first heading need no qualifier
const sections = computed<SubstitutionSection[]>(() => [
  {
    key: "recipe",
    title: i18n.t("recipe.substitutions"),
    items: recipeSubstitutions.value,
    dimmed: false,
  },
  {
    key: "food",
    title: i18n.t("recipe.commonly-substituted-with"),
    items: foodSubstitutions.value,
    dimmed: true,
  },
].filter(section => section.items.length));
</script>

<style lang="scss" scoped>
.ingredient-substitutions {
  .substitution-header {
    border-bottom: thin solid rgba(var(--v-theme-on-surface), 0.12);
    padding-bottom: 0.2rem;
    margin-bottom: 0.4rem;
  }

  .substitution {
    line-height: 1.35;

    & + .substitution {
      margin-top: 0.5rem;
    }
  }

  .substitution-primary {
    font-weight: bold;
  }

  // matches the dimming the ingredient note already uses
  .substitution-note {
    opacity: 0.7;
  }

  .substitution-primary,
  .substitution-note {
    :deep(p) {
      display: inline;
      margin: 0;
    }
  }

  .food-substitutions {
    opacity: 0.7;
  }
}
</style>
