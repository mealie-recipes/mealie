<template>
  <div class="text-center">
    <v-menu offset-y top nudge-top="6" :close-on-content-click="false">
      <template #activator="{ on, attrs }">
        <v-btn color="accent" dark v-bind="attrs" v-on="on">
          <v-icon left>
            {{ $globals.icons.cog }}
          </v-icon>
          {{ $t("general.settings") }}
        </v-btn>
      </template>
      <v-card>
        <v-card-title class="py-2">
          <div>
            {{ $t("recipe.recipe-settings") }}
          </div>
        </v-card-title>
        <v-divider class="mx-2"></v-divider>
        <v-card-text class="mt-n5 pt-6 pb-2">
          <v-switch
            v-for="(itemValue, key) in value"
            :key="key"
            v-model="value[key]"
            xs
            dense
            :disabled="key == 'locked' && !isOwner"
            class="my-1"
            :label="labels[key]"
            hide-details
          ></v-switch>
        </v-card-text>
      </v-card>
    </v-menu>
  </div>
</template>

<script lang="ts">
import { defineComponent, useContext } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    value: {
      type: Object,
      required: true,
    },
    isOwner: {
      type: Boolean,
      required: false,
    },
  },
  setup() {
    const { i18n } = useContext();
    const labels = {
      public: i18n.t("recipe.public-recipe"),
      showNutrition: i18n.t("recipe.show-nutrition-values"),
      showAssets: i18n.t("asset.show-assets"),
      landscapeView: i18n.t("recipe.landscape-view-coming-soon"),
      disableComments: i18n.t("recipe.disable-comments"),
      disableAmount: i18n.t("recipe.disable-amount"),
      locked: "Locked",
    };

    return {
      labels,
    }
  },
});
</script>

<style lang="scss" scoped></style>
