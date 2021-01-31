<template>
  <v-navigation-drawer width="175px" clipped app permanent expand-on-hover>
    <v-list nav dense>
      <v-list-item v-for="nav in links" :key="nav.title" link :to="nav.to">
        <v-list-item-icon>
          <v-icon>{{ nav.icon }}</v-icon>
        </v-list-item-icon>
        <v-list-item-title>{{ nav.title }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
export default {
  data() {
    return {
      links: [
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
  },
  mounted() {
    this.allCategories.forEach(async (element) => {
      this.links.push({
        title: element,
        to: `/recipes/${element}`,
        icon: "mdi-tag",
      });
    });
  },
};
</script>

<style>
</style>