<template>
  <div>
    <v-btn
      class="mt-9 ml-n1"
      fixed
      left
      bottom
      fab
      small
      color="primary"
      @click="showSidebar = !showSidebar"
    >
      <v-icon>mdi-tag</v-icon></v-btn
    >

    <v-navigation-drawer
      :value="mobile ? showSidebar : true"
      v-model="showSidebar"
      width="175px"
      clipped
      app
    >
      <v-list nav dense>
        <v-list-item v-for="nav in links" :key="nav.title" link :to="nav.to">
          <v-list-item-icon>
            <v-icon>{{ nav.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-title>{{ nav.title | titleCase }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>
  </div>
</template>

<script>
import { api } from "@/api";
export default {
  data() {
    return {
      showSidebar: false,
      mobile: false,
      links: [],
      baseLinks: [
        {
          icon: "mdi-home",
          to: "/",
          title: this.$t("page.home-page"),
        },
        {
          icon: "mdi-view-module",
          to: "/recipes/all",
          title: this.$t("page.all-recipes"),
        },
        {
          icon: "mdi-magnify",
          to: "/search",
          title: this.$t('search.search'),
        },
      ],
    };
  },
  computed: {
    allCategories() {
      return this.$store.getters.getCategories;
    },
  },
  watch: {
    allCategories() {
      this.buildSidebar();
    },
    showSidebar() {},
  },
  mounted() {
    this.buildSidebar();
    this.mobile = this.viewScale();
    this.showSidebar = !this.viewScale();
  },

  methods: {
    async buildSidebar() {
      this.links = [];
      this.links.push(...this.baseLinks);
      const pages = await api.siteSettings.getPages();
      pages.sort((a, b) => a.position - b.position);
      pages.forEach(async element => {
        this.links.push({
          title: element.name,
          to: `/pages/${element.slug}`,
          icon: "mdi-tag",
        });
      });
    },
    viewScale() {
      switch (this.$vuetify.breakpoint.name) {
        case "xs":
          return true;
        case "sm":
          return true;
        default:
          return false;
      }
    },
  },
};
</script>

<style>
</style>