<template>
  <div>
    <v-switch
      v-for="(_, key) in model"
      :key="key"
      v-model="model[key]"
      color="primary"
      xs
      density="compact"
      :disabled="key == 'locked' && !isOwner"
      class="my-1"
      :label="labels[key]"
      hide-details
    />
  </div>
</template>

<script lang="ts" setup>
import { defineModel, defineProps } from "vue";
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
  disableAmount: i18n.t("recipe.disable-amount"),
  locked: i18n.t("recipe.locked"),
};
</script>

<style lang="scss" scoped></style>
