<template>
  <div>
    <v-switch
      v-for="(_, key) in value"
      :key="key"
      v-model="value[key]"
      xs
      dense
      :disabled="key == 'locked' && !isOwner"
      class="my-1"
      :label="labels[key]"
      hide-details
    ></v-switch>
  </div>
</template>

<script lang="ts">
import { defineComponent, useContext } from "@nuxtjs/composition-api";
import { RecipeSettings } from "~/lib/api/types/recipe";

export default defineComponent({
  props: {
    value: {
      type: Object as () => RecipeSettings,
      required: true,
    },
    isOwner: {
      type: Boolean,
      required: false,
    },
  },
  setup() {
    const { i18n } = useContext();
    const labels: Record<keyof RecipeSettings, string> = {
      public: i18n.tc("recipe.public-recipe"),
      showNutrition: i18n.tc("recipe.show-nutrition-values"),
      showAssets: i18n.tc("asset.show-assets"),
      landscapeView: i18n.tc("recipe.landscape-view-coming-soon"),
      disableComments: i18n.tc("recipe.disable-comments"),
      disableAmount: i18n.tc("recipe.disable-amount"),
      locked: i18n.tc("recipe.locked"),
    };

    return {
      labels,
    };
  },
});
</script>

<style lang="scss" scoped></style>
