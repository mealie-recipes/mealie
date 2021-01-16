<template>
  <v-app>
    <v-app-bar dense app color="primary" dark class="d-print-none">
      <v-btn @click="$router.push('/')" icon>
        <v-icon size="40"> mdi-silverware-variant </v-icon>
      </v-btn>
      <div btn class="pl-2">
        <v-toolbar-title @click="$router.push('/')">Mealie</v-toolbar-title>
      </div>

      <v-spacer></v-spacer>
      <v-expand-x-transition>
        <SearchBar
          class="mt-7"
          v-if="search"
          :show-results="true"
          @selected="navigateFromSearch"
        />
      </v-expand-x-transition>
      <v-btn icon @click="toggleSearch">
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

  mounted() {
    this.$store.dispatch("initTheme");
    this.$store.dispatch("requestRecentRecipes");
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

    toggleSearch() {
      if (this.search === true) {
        this.search = false;
      } else {
        this.search = true;
      }
    },
    navigateFromSearch(slug) {
      this.$router.push(`/recipe/${slug}`);
    },
  },
};
</script>

<style>
/* Scroll Bar PageSettings */
body::-webkit-scrollbar {
  width: 0.25rem;
}

body::-webkit-scrollbar-track {
  background: grey;
}

body::-webkit-scrollbar-thumb {
  background: black;
}
</style>
