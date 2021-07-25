<template>
  <v-app>
    <!-- Dummpy Comment -->
    <TheAppBar />
    <v-main>
      <v-banner v-if="demo" sticky>
        <div class="text-center">
          <b> This is a Demo of the v0.5.0 (BETA) </b> | Username: changeme@email.com | Password: demo
        </div>
      </v-banner>
      <GlobalSnackbar />
      <v-snackbar v-model="snackWithButtons" bottom left timeout="-1">
        {{ snackWithBtnText }}
        <template v-slot:action="{ attrs }">
          <v-btn text color="primary" v-bind="attrs" @click.stop="refreshApp">
            {{ snackBtnText }}
          </v-btn>
          <v-btn icon class="ml-4" @click="snackWithButtons = false">
            <v-icon>{{ $globals.icons.close }}</v-icon>
          </v-btn>
        </template>
      </v-snackbar>
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

  async created() {
    // Initial API Requests
    this.$store.dispatch("initTheme");
    this.$store.dispatch("refreshToken");
    this.$store.dispatch("requestUserData");
    this.$store.dispatch("requestCurrentGroup");
    this.$store.dispatch("requestTags");
    this.$store.dispatch("requestAppInfo");
    this.$store.dispatch("requestSiteSettings");

    // Listen for swUpdated event and display refresh snackbar as required.
    document.addEventListener("swUpdated", this.showRefreshUI, { once: true });
    // Refresh all open app tabs when a new service worker is installed.
    if (navigator.serviceWorker) {
      navigator.serviceWorker.addEventListener("controllerchange", () => {
        if (this.refreshing) return;
        this.refreshing = true;
        window.location.reload();
      });
    }
  },

  mounted() {
    this.darkModeSystemCheck();
    this.darkModeAddEventListener();
  },

  data() {
    return {
      refreshing: false,
      registration: null,
      snackBtnText: "",
      snackWithBtnText: "",
      snackWithButtons: false,
    };
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

    showRefreshUI(e) {
      // Display a snackbar inviting the user to refresh/reload the app due
      // to an app update being available.
      // The new service worker is installed, but not yet active.
      // Store the ServiceWorkerRegistration instance for later use.
      this.registration = e.detail;
      this.snackBtnText = this.$t("events.refresh");
      this.snackWithBtnText = this.$t("events.new-version");
      this.snackWithButtons = true;
    },
    refreshApp() {
      this.snackWithButtons = false;
      // Protect against missing registration.waiting.
      if (!this.registration || !this.registration.waiting) {
        return;
      }
      this.registration.waiting.postMessage("skipWaiting");
    },
  },
};
</script>

<style>
.top-dialog {
  align-self: flex-start;
}
:root {
  scrollbar-color: transparent transparent;
}
</style>

