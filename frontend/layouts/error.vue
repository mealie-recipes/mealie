<template>
  <div>
    <v-card-title>
      <slot>
        <h1 class="mx-auto">{{ $t("page.404-page-not-found") }}</h1>
      </slot>
    </v-card-title>
    <div class="d-flex justify-space-around">
      <div class="d-flex align-center">
        <p class="primary--text">4</p>
        <v-icon color="primary" class="mx-auto mb-0" size="200">
          {{ $globals.icons.primary }}
        </v-icon>
        <p class="primary--text">4</p>
      </div>
    </div>
    <v-card-actions>
      <v-spacer></v-spacer>
      <slot name="actions">
        <v-btn v-for="(button, index) in buttons" :key="index" nuxt :to="button.to" color="primary">
          <v-icon left> {{ button.icon }} </v-icon>
          {{ button.text }}
        </v-btn>
      </slot>
      <v-spacer></v-spacer>
    </v-card-actions>
  </div>
</template>

<script lang="ts">
import { defineComponent, useContext, useMeta } from "@nuxtjs/composition-api";

export default defineComponent({
  layout: "basic",
  props: {
    error: {
      type: Object,
      default: null,
    },
  },
  setup(props) {
    useMeta({ title: props.error.statusCode === 404 ? "404 Not Found" : "An error occurred" });

    const { $globals, i18n } = useContext();
    const buttons = [
      { icon: $globals.icons.home, to: "/", text: i18n.t("general.home") },
      { icon: $globals.icons.primary, to: "/recipes/all", text: i18n.t("page.all-recipes") },
      { icon: $globals.icons.search, to: "/search", text: i18n.t("search.search") },
    ];

    return {
      buttons,
    }
  },
  // Needed for useMeta
  head: {},
});
</script>

<style scoped>
h1 {
  font-size: 20px;
}
p {
  padding-bottom: 0 !important;
  margin-bottom: 0 !important;
  font-size: 200px;
}
</style>

