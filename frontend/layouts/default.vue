<template>
  <v-app dark>
    <!-- <TheSnackbar /> -->

    <AppSidebar v-model="sidebar" absolute :top-link="topLinks" @input="sidebar = !sidebar" />

    <AppHeader>
      <v-btn icon @click.stop="sidebar = !sidebar">
        <v-icon> {{ $globals.icons.menu }}</v-icon>
      </v-btn>
    </AppHeader>
    <v-main>
      <v-scroll-x-transition>
        <Nuxt />
      </v-scroll-x-transition>
    </v-main>
    <AppFloatingButton absolute />
  </v-app>
</template>
  

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import AppHeader from "@/components/Layout/AppHeader.vue";
import AppSidebar from "@/components/Layout/AppSidebar.vue";
import AppFloatingButton from "@/components/Layout/AppFloatingButton.vue";

export default defineComponent({
  components: { AppHeader, AppSidebar, AppFloatingButton },
  // @ts-ignore
  // middleware: process.env.GLOBAL_MIDDLEWARE,
  setup() {
    return {};
  },
  data() {
    return {
      sidebar: null,
      topLinks: [
        {
          icon: this.$globals.icons.home,
          to: "/",
          title: this.$t("sidebar.home-page"),
        },
        {
          icon: this.$globals.icons.search,
          to: "/search",
          title: this.$t("sidebar.search"),
        },
        {
          icon: this.$globals.icons.viewModule,
          to: "/recipes/all",
          title: this.$t("sidebar.all-recipes"),
        },
        {
          icon: this.$globals.icons.tags,
          to: "/recipes/categories",
          title: this.$t("sidebar.categories"),
        },
        {
          icon: this.$globals.icons.tags,
          to: "/recipes/tags",
          title: this.$t("sidebar.tags"),
        },
      ],
    };
  },
  head: {
    title: "Home",
  },
});
</script>
      
      <style scoped>
</style>+