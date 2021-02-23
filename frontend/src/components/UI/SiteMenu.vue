<template>
  <div class="text-center">
    <LoginDialog ref="loginDialog" />
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
  data: function() {
    return {
      items: [
        {
          icon: "mdi-account",
          title: "Login",
          restricted: false,
          login: true,
        },
        {
          icon: "mdi-account",
          title: "Logout",
          restricted: true,
          login: true,
        },
        {
          icon: "mdi-calendar-week",
          title: this.$i18n.t("meal-plan.dinner-this-week"),
          nav: "/meal-plan/this-week",
          restricted: true,
        },
        {
          icon: "mdi-calendar-today",
          title: this.$i18n.t("meal-plan.dinner-today"),
          nav: "/meal-plan/today",
          restricted: true,
        },
        {
          icon: "mdi-calendar-multiselect",
          title: this.$i18n.t("meal-plan.planner"),
          nav: "/meal-plan/planner",
          restricted: true,
        },
        {
          icon: "mdi-cog",
          title: this.$i18n.t("general.settings"),
          nav: "/admin",
          restricted: true,
        },
      ],
    };
  },
  mounted() {},
  computed: {
    loggedIn() {
      return this.$store.getters.getIsLoggedIn;
    },
    filteredItems() {
      if (this.loggedIn) {
        return this.items.filter(x => x.restricted == true);
      } else {
        return this.items.filter(x => x.restricted == false);
      }
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