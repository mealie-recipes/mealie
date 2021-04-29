<template>
  <div>
    <v-card flat>
      <v-tabs
        v-model="tab"
        background-color="primary"
        centered
        dark
        icons-and-text
      >
        <v-tabs-slider></v-tabs-slider>

        <v-tab>
          {{ $t("recipe.categories") }}
          <v-icon>mdi-tag-multiple-outline</v-icon>
        </v-tab>

        <v-tab>
          {{ $t("tag.tags") }}
          <v-icon>mdi-tag-multiple-outline</v-icon>
        </v-tab>
      </v-tabs>

      <v-tabs-items v-model="tab">
        <v-tab-item><CategoryTagEditor :is-tags="false"/></v-tab-item>
        <v-tab-item><CategoryTagEditor :is-tags="true" /> </v-tab-item>
      </v-tabs-items>
    </v-card>
  </div>
</template>

<script>
import CategoryTagEditor from "./CategoryTagEditor";
export default {
  components: {
    CategoryTagEditor,
  },
  data() {
    return {
      tab: 0,
    };
  },
};
</script>

<style>
</style>