<template>
  <div>
    <v-card flat>
      <v-tabs v-model="tab" background-color="primary" centered dark icons-and-text show-arrows>
        <v-tabs-slider></v-tabs-slider>

        <v-tab href="#event-notifications">
          {{ $t("settings.notify") }}
          <v-icon>{{ $globals.icons.bellAlert }}</v-icon>
        </v-tab>
        <v-tab href="#category-editor">
          {{ $t("recipe.categories") }}
          <v-icon>{{ $globals.icons.tags }}</v-icon>
        </v-tab>

        <v-tab href="#tag-editor">
          {{ $t("tag.tags") }}
          <v-icon>{{ $globals.icons.tags }}</v-icon>
        </v-tab>
        <v-tab href="#organize">
          {{ $t("settings.organize") }}
          <v-icon>{{ $globals.icons.broom }}</v-icon>
        </v-tab>
      </v-tabs>

      <v-tabs-items v-model="tab">
        <v-tab-item value="event-notifications"> <EventNotification /></v-tab-item>
        <v-tab-item value="category-editor"> <CategoryTagEditor :is-tags="false"/></v-tab-item>
        <v-tab-item value="tag-editor"> <CategoryTagEditor :is-tags="true" /> </v-tab-item>
        <v-tab-item value="organize"> <RecipeOrganizer /> </v-tab-item>
      </v-tabs-items>
    </v-card>
  </div>
</template>

<script>
import EventNotification from "./EventNotification";
import CategoryTagEditor from "./CategoryTagEditor";
import RecipeOrganizer from "./RecipeOrganizer";
export default {
  components: {
    CategoryTagEditor,
    EventNotification,
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
