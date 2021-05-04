<template>
  <div>
    <v-card flat>
      <v-tabs v-model="tab" background-color="primary" centered dark icons-and-text>
        <v-tabs-slider></v-tabs-slider>

        <v-tab href="#category-editor">
          {{ $t("recipe.categories") }}
          <v-icon>mdi-tag-multiple-outline</v-icon>
        </v-tab>

        <v-tab href="#tag-editor">
          {{ $t("tag.tags") }}
          <v-icon>mdi-tag-multiple-outline</v-icon>
        </v-tab>
        <v-tab href="#organize">
          Organize
          <v-icon>mdi-broom</v-icon>
        </v-tab>
      </v-tabs>

      <v-tabs-items v-model="tab">
        <v-tab-item value="category-editor"> <CategoryTagEditor :is-tags="false"/></v-tab-item>
        <v-tab-item value="tag-editor"> <CategoryTagEditor :is-tags="true" /> </v-tab-item>
        <v-tab-item value="organize"> <RecipeOrganizer :is-tags="true" /> </v-tab-item>
      </v-tabs-items>
    </v-card>
  </div>
</template>

<script>
import CategoryTagEditor from "./CategoryTagEditor";
import RecipeOrganizer from "./RecipeOrganizer";
export default {
  components: {
    CategoryTagEditor,
    RecipeOrganizer,
  },
  computed: {
    tab: {
      set(tab) {
        this.$router.replace({ query: { ...this.$route.query, tab } });
      },
      get() {
        return this.$route.query.tab;
      },
    },
  },
  data() {
    return {};
  },
};
</script>

<style></style>
