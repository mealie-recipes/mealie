<template>
  <v-app>
    <v-app-bar clipped-left dense app color="primary" dark class="d-print-none">
      <router-link to="/">
        <v-btn icon>
          <v-icon size="40"> mdi-silverware-variant </v-icon>
        </v-btn>
      </router-link>

      <div btn class="pl-2">
        <v-toolbar-title style="cursor: pointer" @click="$router.push('/')"
          >Mealie
        </v-toolbar-title>
      </div>

      <v-spacer></v-spacer>
      <v-expand-x-transition>
        <SearchBar
          ref="mainSearchBar"
          class="mt-7"
          v-if="search"
          :show-results="true"
          @selected="navigateFromSearch"
        />
      </v-expand-x-transition>
      <v-btn icon @click="search = !search">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>

      <Menu />
    </v-app-bar>
    <v-main>
      <v-container>
        <AddRecipeFab />
        <SnackBar />
        <router-view></router-view>
      </v-container>
      <FlashMessage :position="'right bottom'"></FlashMessage>
    </v-main>
  </v-app>
</template>

<script>
import Menu from "./components/UI/Menu";
import SearchBar from "./components/UI/SearchBar";
import AddRecipeFab from "./components/UI/AddRecipeFab";
import SnackBar from "./components/UI/SnackBar";
import Vuetify from "./plugins/vuetify";
export default {
  name: "App",

  components: {
    Menu,
    AddRecipeFab,
    SnackBar,
    SearchBar,
  },

  watch: {
    $route() {
      this.search = false;
    },
  },
  created() {
    window.addEventListener("keyup", e => {
      if (e.key == "/" && !document.activeElement.id.startsWith('input') ) {
        this.search = !this.search;
      }
    });
  },

  mounted() {
    this.$store.dispatch("initTheme");
    this.$store.dispatch("requestRecentRecipes");
    this.$store.dispatch("requestHomePageSettings");
    this.$store.dispatch("initLang");
    this.darkModeSystemCheck();
    this.darkModeAddEventListener();
  },

  data: () => ({
    search: false,
  }),
  methods: {
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

</style>
