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
        <v-list-item v-for="(item, i) in items" :key="i" link :to="item.nav">
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
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
  data: function() {
    return {
      items: [
        {
          icon: "mdi-calendar-week",
          title: this.$i18n.t("meal-plan.dinner-this-week"),
          nav: "/meal-plan/this-week",
        },
        {
          icon: "mdi-calendar-today",
          title: this.$i18n.t("meal-plan.dinner-today"),
          nav: "/meal-plan/today",
        },
        {
          icon: "mdi-calendar-multiselect",
          title: this.$i18n.t("meal-plan.planner"),
          nav: "/meal-plan/planner",
        },
        {
          icon: "mdi-cog",
          title: this.$i18n.t("general.settings"),
          nav: "/settings/site",
        },
      ],
    };
  },
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