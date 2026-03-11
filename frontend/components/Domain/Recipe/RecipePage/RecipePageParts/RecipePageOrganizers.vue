<template>
  <div>
    <!-- Recipe Categories -->
    <v-card
      v-if="recipe.recipeCategory.length > 0 || isEditForm"
      :class="{ 'mt-10': !isEditForm }"
    >
      <v-card-title class="py-2">
        {{ $t("recipe.categories") }}
      </v-card-title>
      <v-divider class="mx-2" />
      <v-card-text>
        <RecipeOrganizerSelector
          v-if="isEditForm"
          v-model="recipe.recipeCategory"
          :return-object="true"
          :show-add="true"
          selector-type="categories"
        />
        <RecipeChips
          v-else
          :items="recipe.recipeCategory"
          v-bind="$attrs"
        />
      </v-card-text>
    </v-card>

    <!-- Recipe Tags -->
    <v-card
      v-if="recipe.tags.length > 0 || isEditForm"
      class="mt-4"
    >
      <v-card-title class="py-2">
        {{ $t("tag.tags") }}
      </v-card-title>
      <v-divider class="mx-2" />
      <v-card-text>
        <RecipeOrganizerSelector
          v-if="isEditForm"
          v-model="recipe.tags"
          :return-object="true"
          :show-add="true"
          selector-type="tags"
        />
        <template v-else>
          <div
            v-for="(section, i) in groupedTagSections"
            :key="section.id"
            :class="{ 'mt-3': i > 0 }"
          >
            <template v-if="section.name">
              <h3 class="mt-2">
                {{ section.name }}
              </h3>
              <v-divider />
            </template>
            <RecipeChips
              :items="section.tags"
              url-prefix="tags"
              v-bind="$attrs"
            />
          </div>
        </template>
      </v-card-text>
    </v-card>

    <!-- Recipe Tools Edit -->
    <v-card
      v-if="isEditForm"
      class="mt-2"
    >
      <v-card-title class="py-2">
        {{ $t('tool.required-tools') }}
      </v-card-title>
      <v-divider class="mx-2" />
      <v-card-text>
        <RecipeOrganizerSelector
          v-model="recipe.tools"
          selector-type="tools"
          v-bind="$attrs"
        />
      </v-card-text>
    </v-card>

    <RecipeNutrition
      v-if="recipe.settings.showNutrition"
      v-model="recipe.nutrition"
      class="mt-4"
      :edit="isEditForm"
    />
    <RecipeAssets
      v-if="recipe.settings.showAssets"
      v-model="recipe.assets"
      :edit="isEditForm"
      :slug="recipe.slug"
      :recipe-id="recipe.id"
    />
  </div>
</template>

<script lang="ts" setup>
import { usePageState } from "~/composables/recipe-page/shared-state";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe, RecipeTag } from "~/lib/api/types/recipe";
import RecipeOrganizerSelector from "@/components/Domain/Recipe/RecipeOrganizerSelector.vue";
import RecipeNutrition from "~/components/Domain/Recipe/RecipeNutrition.vue";
import RecipeChips from "@/components/Domain/Recipe/RecipeChips.vue";
import RecipeAssets from "@/components/Domain/Recipe/RecipeAssets.vue";
import { useTagGroupStore } from "~/composables/store";

const recipe = defineModel<NoUndefinedField<Recipe>>({ required: true });
const { isEditForm } = usePageState(recipe.value.slug);

const { store: tagGroups } = useTagGroupStore();

const groupedTagSections = computed(() => {
  // bucket tags by tagGroupId
  const byGroup: Record<string, RecipeTag[]> = {};
  for (const tag of recipe.value.tags as RecipeTag[]) {
    const key = tag.tagGroupId ?? "__ungrouped__";
    if (!byGroup[key]) byGroup[key] = [];
    byGroup[key].push(tag);
  }

  const sections: { id: string; name: string; color: string | null; tags: RecipeTag[] }[] = [];

  // known groups, sorted by position
  for (const group of [...tagGroups.value]
    .filter(g => byGroup[g.id]?.length > 0)
    .sort((a, b) => a.position - b.position || a.name.localeCompare(b.name))) {
    sections.push({ id: group.id, name: group.name, color: group.color ?? null, tags: byGroup[group.id] });
  }

  // ungrouped at the end, no label
  if (byGroup["__ungrouped__"]?.length > 0) {
    sections.push({ id: "__ungrouped__", name: "", color: null, tags: byGroup["__ungrouped__"] });
  }

  return sections;
});
</script>
