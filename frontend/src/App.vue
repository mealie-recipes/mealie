<template>
  <v-app>
    <!-- Dummpy Comment -->
    <TheAppBar />
    <v-main>
      <v-banner v-if="!demo" sticky>
        <div class="text-center"><b> This is a Demo of the v0.5.0 (BETA) </b> | Username: changeme@email.com | Password: demo</div>
      </v-banner>
      <GlobalSnackbar />
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
import TheAppBar from "@/components/UI/TheAppBar";
import GlobalSnackbar from "@/components/UI/GlobalSnackbar";
import Vuetify from "./plugins/vuetify";
import { user } from "@/mixins/user";

export default {
  name: "App",

  components: {
    TheAppBar,
    GlobalSnackbar,
  },

  mixins: [user],

  computed: {
    demo() {
      const appInfo = this.$store.getters.getAppInfo;
      return appInfo.demoStatus;
    },
  },

  async mounted() {
    this.$store.dispatch("initTheme");
    this.$store.dispatch("requestRecentRecipes");
    this.$store.dispatch("refreshToken");
    this.$store.dispatch("requestCurrentGroup");
    this.$store.dispatch("requestCategories");
    this.$store.dispatch("requestTags");
    this.darkModeSystemCheck();
    this.darkModeAddEventListener();
    this.$store.dispatch("requestAppInfo");
    this.$store.dispatch("requestCustomPages");
    this.$store.dispatch("requestSiteSettings");
  },

  methods: {
    // For Later!

    /**
     * Checks if 'system' is set for dark mode and then sets the corrisponding value for vuetify
     */
    darkModeSystemCheck() {
      if (this.$store.getters.getDarkMode === "system")
        Vuetify.framework.theme.dark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    },
    /**
     * This will monitor the OS level darkmode and call to update dark mode.
     */
    darkModeAddEventListener() {
      const darkMediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      darkMediaQuery.addEventListener("change", () => {
        this.darkModeSystemCheck();
      });
    },
  },
};
</script>

<style>
:root {
  scrollbar-color: transparent transparent;
}
</style>
