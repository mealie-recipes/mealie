<template>
  <div class="text-center">
    <v-menu
      transition="slide-x-transition"
      bottom
      right
      offset-y
      open-on-hover
      close-delay="200"
    >
      <template v-slot:activator="{ on, attrs }">
        <v-btn v-bind="attrs" v-on="on" icon>
          <v-icon>mdi-menu</v-icon>
        </v-btn>
      </template>

      <v-list>
        <v-list-item v-for="(item, i) in items" :key="i" link>
          <v-list-item-icon @click="navRouter(item.nav)">
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-content @click="navRouter(item.nav)">
            <v-list-item-title>
              {{ item.title }}
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script>
export default {
  data: () => ({
    items: [
      {
        icon: "mdi-calendar-week",
        title: "Dinner This Week",
        nav: "/meal-plan/this-week",
      },
      {
        icon: "mdi-calendar-today",
        title: "Dinner Today",
        nav: "/meal-plan/today",
      },
      {
        icon: "mdi-calendar-multiselect",
        title: "Planner",
        nav: "/meal-plan/planner",
      },
      { icon: "mdi-cog", title: "Settings", nav: "/settings/site" },
    ],
  }),
  methods: {
    navRouter(route) {
      this.$router.push(route);
    },
  },
};
</script>
<style>
.menu-text {
  text-align: left !important;
}
</style>