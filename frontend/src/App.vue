<template>
  <v-app>
    <v-app-bar clipped-left dense app color="primary" dark class="d-print-none">
      <router-link v-if="!(isMobile && search)" to="/">
        <v-btn icon>
          <v-icon size="40"> mdi-silverware-variant </v-icon>
        </v-btn>
      </router-link>

      <div v-if="!isMobile" btn class="pl-2">
        <v-toolbar-title style="cursor: pointer" @click="$router.push('/')"
          >Mealie
        </v-toolbar-title>
      </div>

      <v-spacer></v-spacer>
      <v-expand-x-transition>
        <SearchBar
          ref="mainSearchBar"
          v-if="search"
          :show-results="true"
          @selected="navigateFromSearch"
          :max-width="isMobile ? '100%' : '450px'"
        />
      </v-expand-x-transition>
      <v-btn icon @click="search = !search">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>

      <SiteMenu />
      <LanguageMenu />
    </v-app-bar>
    <v-main>
      <v-banner v-if="demo" sticky
        ><div class="text-center">
          <b> This is a Demo</b> | Username: changeme@email.com | Password: demo
        </div></v-banner
      >

      <v-slide-x-reverse-transition>
        <AddRecipeFab v-if="loggedIn" />
      </v-slide-x-reverse-transition>
      <router-view></router-view>
    </v-main>
    <FlashMessage :position="'right bottom'"></FlashMessage>
  </v-app>
</template>

<script>
import SiteMenu from "@/components/UI/SiteMenu";
import SearchBar from "@/components/UI/Search/SearchBar";
import AddRecipeFab from "@/components/UI/AddRecipeFab";
import LanguageMenu from "@/components/UI/LanguageMenu";
import Vuetify from "./plugins/vuetify";
import { user } from "@/mixins/user";
import { api } from "./api";

export default {
  name: "App",

  components: {
    SiteMenu,
    AddRecipeFab,
    SearchBar,
    LanguageMenu,
  },

  mixins: [user],

  watch: {
    $route() {
      this.search = false;
    },
  },
  computed: {
    isMobile() {
      return this.$vuetify.breakpoint.name === "xs";
    },
  },

  created() {
    window.addEventListener("keyup", e => {
      if (e.key == "/" && !document.activeElement.id.startsWith("input")) {
        this.search = !this.search;
      }
    });
    this.$store.dispatch("initLang", { currentVueComponent: this });
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

    const api_status = await api.meta.getIsDemo();
    this.demo = api_status.demoStatus;
  },

  data: () => ({
    search: false,
    demo: false,
  }),
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
    navigateFromSearch(slug) {
      this.$router.push(`/recipe/${slug}`);
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

.notify-base {
  color: white !important;
  margin-right: 60px;
  margin-bottom: -5px;
  opacity: 0.9 !important;
}
</style>
