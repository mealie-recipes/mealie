<template>
  <v-menu offset-y offset-overflow left top nudge-top="6" :close-on-content-click="false">
    <template #activator="{ on, attrs }">
      <v-btn color="accent" dark v-bind="attrs" v-on="on">
        <v-icon left>
          {{ $globals.icons.foods }}
        </v-icon>
        Parse
      </v-btn>
    </template>
    <v-card width="400">
      <v-card-title class="mb-1 pb-0">
        <v-icon left color="warning"> {{ $globals.icons.alert }}</v-icon> Experimental
      </v-card-title>
      <v-divider class="mx-2"> </v-divider>
      <v-card-text>
        Mealie can use natural language processing to attempt to parse and create units, and foods for your Recipe
        ingredients. This is experimental and may not work as expected. If you choose to not use the parsed results you
        can click the close button at the top of the page and your changes will not be saved.
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <BaseButton small color="accent" :to="`${slug}/ingredient-parser`">
          <template #icon>
            {{ $globals.icons.check }}
          </template>
          {{ $t("general.confirm") }}
        </BaseButton>
      </v-card-actions>
    </v-card>
  </v-menu>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    ingredients: {
      type: Array,
      required: true,
    },
    slug: {
      type: String,
      required: true,
    },
  },
  setup() {
    return {};
  },
});
</script>
