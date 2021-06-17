<template>
  <div class="text-center">
    <LoginDialog ref="loginDialog" />
    <v-menu transition="slide-x-transition" bottom right offset-y offset-overflow open-on-hover close-delay="200">
      <template v-slot:activator="{ on, attrs }">
        <v-btn v-bind="attrs" v-on="on" icon>
          <v-icon>{{ $globals.icons.user }}</v-icon>
        </v-btn>
      </template>

      <v-list>
        <v-list-item
          v-for="(item, i) in filteredItems"
          :key="i"
          link
          :to="item.nav ? item.nav : null"
          @click="item.login ? openLoginDialog() : null"
        >
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
import LoginDialog from "../Login/LoginDialog";
export default {
  components: {
    LoginDialog,
  },
  computed: {
    items() {
      return [
        {
          icon: this.$globals.icons.user,
          title: this.$t("user.login"),
          restricted: false,
          login: true,
        },
        {
          icon: this.$globals.icons.calendarWeek,
          title: this.$t("meal-plan.dinner-this-week"),
          nav: "/meal-plan/this-week",
          restricted: true,
        },
        {
          icon: this.$globals.icons.calendarToday,
          title: this.$t("meal-plan.dinner-today"),
          nav: "/meal-plan/today",
          restricted: true,
        },
        {
          icon: this.$globals.icons.calendarMultiselect,
          title: this.$t("meal-plan.planner"),
          nav: "/meal-plan/planner",
          restricted: true,
        },
        {
          icon: this.$globals.icons.formatListCheck,
          title: this.$t("shopping-list.shopping-lists"),
          nav: "/shopping-list",
          restricted: true,
        },
        {
          icon: this.$globals.icons.logout,
          title: this.$t("user.logout"),
          restricted: true,
          nav: "/logout",
        },
        {
          icon: this.$globals.icons.cog,
          title: this.$t("general.settings"),
          nav: "/admin",
          restricted: true,
        },
      ];
    },
    filteredItems() {
      if (this.loggedIn) {
        return this.items.filter(x => x.restricted == true);
      } else {
        return this.items.filter(x => x.restricted == false);
      }
    },
    loggedIn() {
      return this.$store.getters.getIsLoggedIn;
    },
  },

  methods: {
    openLoginDialog() {
      this.$refs.loginDialog.open();
    },
  },
};
</script>
<style>
.menu-text {
  text-align: left !important;
}
</style>
