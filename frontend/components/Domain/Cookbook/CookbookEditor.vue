<template>
  <div>
    <v-card-text v-if="cookbook">
      <v-text-field v-model="cookbook.name" :label="$t('cookbook.cookbook-name')"></v-text-field>
      <v-textarea v-model="cookbook.description" auto-grow :rows="2" :label="$t('recipe.description')"></v-textarea>
      <RecipeOrganizerSelector v-model="cookbook.categories" selector-type="categories" />
      <RecipeOrganizerSelector v-model="cookbook.tags" selector-type="tags" />
      <RecipeOrganizerSelector v-model="cookbook.tools" selector-type="tools" />
      <v-switch v-model="cookbook.public" hide-details single-line>
        <template #label>
          {{ $t('cookbook.public-cookbook') }}
          <HelpIcon small right class="ml-2">
            {{ $t('cookbook.public-cookbook-description') }}
          </HelpIcon>
        </template>
      </v-switch>
      <div class="mt-4">
        <h3 class="text-subtitle-1 d-flex align-center mb-0 pb-0">
          {{ $t('cookbook.filter-options') }}
          <HelpIcon right small class="ml-2">
            {{ $t('cookbook.filter-options-description') }}
          </HelpIcon>
        </h3>
        <v-switch v-model="cookbook.requireAllCategories" class="mt-0" hide-details single-line>
          <template #label> {{ $t('cookbook.require-all-categories') }} </template>
        </v-switch>
        <v-switch v-model="cookbook.requireAllTags" hide-details single-line>
          <template #label> {{ $t('cookbook.require-all-tags') }} </template>
        </v-switch>
        <v-switch v-model="cookbook.requireAllTools" hide-details single-line>
          <template #label> {{ $t('cookbook.require-all-tools') }} </template>
        </v-switch>
      </div>
    </v-card-text>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { ReadCookBook } from "~/lib/api/types/cookbook";
import RecipeOrganizerSelector from "~/components/Domain/Recipe/RecipeOrganizerSelector.vue";
export default defineComponent({
  components: { RecipeOrganizerSelector },
  props: {
    cookbook: {
      type: Object as () => ReadCookBook,
      required: true,
    },
    actions: {
      type: Object as () => any,
      required: true,
    },
  },
});
</script>
