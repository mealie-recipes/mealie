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
export default {
  data() {
    return {
      showSidebar: false,
      links: [],
      baseLinks: [
        {
          icon: "mdi-home",
          to: "/",
          title: "Home",
        },
        {
          icon: "mdi-view-module",
          to: "/recipes/all",
          title: "All Recipes",
        },
      ],
    };
  },
  computed: {
    allCategories() {
      return this.$store.getters.getCategories;
    },
    mobile() {
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
  watch: {
    allCategories() {
      this.buildSidebar();
    },
  },
  mounted() {
    this.buildSidebar();
  },

  methods: {
    async buildSidebar() {
      this.links = [];
      this.links.push(...this.baseLinks);
      this.allCategories.forEach(async element => {
        this.links.push({
          title: element.name,
          to: `/recipes/${element.slug}`,
          icon: "mdi-tag",
        });
      });
    },
  },
};
</script>

<style>
</style>