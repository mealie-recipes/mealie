<template>
  <v-app> 
    <!-- Dummpy Comment -->
    <TheAppBar />
    <v-main>
      <v-banner v-if="demo" sticky
        ><div class="text-center">
          <b> This is a Demo</b> | Username: changeme@email.com | Password: demo
        </div></v-banner
      >

      <v-slide-x-reverse-transition>
        <TheRecipeFab v-if="loggedIn" />
      </v-slide-x-reverse-transition>
      <router-view></router-view>
    </v-main>
    <FlashMessage :position="'right bottom'"></FlashMessage>
  </v-app>
</template>

<script>
import TheAppBar from "@/components/UI/TheAppBar";
import TheRecipeFab from "@/components/UI/TheRecipeFab";
import Vuetify from "./plugins/vuetify";
import { user } from "@/mixins/user";

export default {
  name: "App",

  components: {
    TheAppBar,
    TheRecipeFab,
  },

  mixins: [user],

  computed: {
    demo() {
      const appInfo = this.$store.getters.getAppInfo;
      return appInfo.demoStatus;
    },
  },

  async created() {
    window.addEventListener("keyup", e => {
      if (e.key == "/" && !document.activeElement.id.startsWith("input")) {
        this.search = !this.search;
      }
    });
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
  },

  methods: {
    // For Later!

    /**
     * Checks if 'system' is set for dark mode and then sets the corrisponding value for vuetify
     */
    darkModeSystemCheck() {
      if (this.$store.getters.getDarkMode === "system")
        Vuetify.framework.theme.dark = window.matchMedia(
          "(prefers-color-scheme: dark)"
        ).matches;
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
.notify-info-color {
  border: 1px, solid, var(--v-info-base) !important;
  border-left: 3px, solid, var(--v-info-base) !important;
  background-color: var(--v-info-base) !important;
}

.notify-warning-color {
  border: 1px, solid, var(--v-warning-base) !important;
  border-left: 3px, solid, var(--v-warning-base) !important;
  background-color: var(--v-warning-base) !important;
}

.notify-error-color {
  border: 1px, solid, var(--v-error-base) !important;
  border-left: 3px, solid, var(--v-error-base) !important;
  background-color: var(--v-error-base) !important;
}

.notify-success-color {
  border: 1px, solid, var(--v-success-base) !important;
  border-left: 3px, solid, var(--v-success-base) !important;
  background-color: var(--v-success-base) !important;
}

.notify-base {
  color: white !important;
  /* min-height: 50px; */
  margin-right: 60px;
  margin-bottom: -5px;
  opacity: 0.9 !important;
}

*::-webkit-scrollbar {
  width: 0.25rem;
}

*::-webkit-scrollbar-track {
  background: lightgray;
}

*::-webkit-scrollbar-thumb {
  background: grey;
}
</style>
