<template>
  <div>
    <div
      v-for="(_, key) in model"
      :key="key"
      class="d-flex align-center"
    >
      <v-switch
        v-model="model[key]"
        color="primary"
        xs
        density="compact"
        :disabled="key == 'locked' && !isOwner"
        class="my-1"
        :label="labels[key]"
        hide-details
      />
      <v-tooltip v-if="key === 'public'" location="bottom">
        <template #activator="{ props: tooltipProps }">
          <v-icon v-bind="tooltipProps" size="small" class="ms-1">
            {{ $globals.icons.informationOutline }}
          </v-icon>
        </template>
        <span>{{ $t('recipe.public-recipe-visibility-note') }}</span>
      </v-tooltip>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RecipeSettings } from "~/lib/api/types/recipe";
import { useI18n } from "#imports";

defineProps<{ isOwner?: boolean }>();

const model = defineModel<RecipeSettings>({ required: true });

const i18n = useI18n();
const labels: Record<keyof RecipeSettings, string> = {
  public: i18n.t("recipe.public-recipe"),
  showNutrition: i18n.t("recipe.show-nutrition-values"),
  showAssets: i18n.t("asset.show-assets"),
  landscapeView: i18n.t("recipe.landscape-view-coming-soon"),
  disableComments: i18n.t("recipe.disable-comments"),
  locked: i18n.t("recipe.locked"),
};
</script>

<style lang="scss" scoped></style>
