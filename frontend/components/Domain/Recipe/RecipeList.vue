<template>
  <v-list>
    <v-list-item v-for="recipe in recipes" :key="recipe.id" :to="'/recipe/' + recipe.slug">
      <v-list-item-avatar>
        <v-icon class="pa-1 primary" dark> {{ $globals.icons.primary }} </v-icon>
      </v-list-item-avatar>
      <v-list-item-content>
        <v-list-item-title>
          {{ recipe.name }}
        </v-list-item-title>
        <v-list-item-subtitle>{{ recipe.description }}</v-list-item-subtitle>
      </v-list-item-content>
      <slot :name="'actions-' + recipe.id" :v-bind="{ item: recipe }"> </slot>
    </v-list-item>
  </v-list>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { RecipeSummary } from "~/types/api-types/recipe";

export default defineComponent({
  props: {
    recipes: {
      type: Array as () => RecipeSummary[],
      required: true,
    },
  },
  setup() {
    return {};
  },
});
</script>