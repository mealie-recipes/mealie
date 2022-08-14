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
          <RecipeSettingsSwitches v-model="value" :is-owner="isOwner" />
        </v-card-text>
      </v-card>
    </v-menu>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import RecipeSettingsSwitches from "./RecipeSettingsSwitches.vue";

export default defineComponent({
  components: { RecipeSettingsSwitches },
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
});
</script>

<style lang="scss" scoped></style>
