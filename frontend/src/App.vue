<template>
  <v-app>
    <v-app-bar dense app color="primary" dark class="d-print-none">
      <div class="d-flex align-center">
        <v-icon size="40" @click="$router.push('/')">
          mdi-silverware-variant
        </v-icon>
      </div>
      <div btn class="pl-2" @click="$router.push('/')">
        <v-toolbar-title>Mealie</v-toolbar-title>
      </div>

      <v-spacer></v-spacer>

      <v-btn icon @click="toggleSearch">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>

      <Menu />
    </v-app-bar>
    <v-main>
      <v-container>
        <AddRecipe />
        <SnackBar />
        <v-expand-transition>
          <SearchHeader v-show="search" />
        </v-expand-transition>

        <router-view></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import Menu from "./components/UI/Menu";
import SearchHeader from "./components/UI/SearchHeader";
import AddRecipe from "./components/AddRecipe";
import SnackBar from "./components/UI/SnackBar";
export default {
  name: "App",

  components: {
    Menu,
    AddRecipe,
    SearchHeader,
    SnackBar,
  },

  watch: {
    $route() {
      this.search = false;
    },
  },

  mounted() {
    this.$store.dispatch("initCookies");
    this.$store.dispatch("requestRecentRecipes");
  },

  data: () => ({
    search: false,
  }),
  methods: {
    toggleSearch() {
      if (this.search === true) {
        this.search = false;
      } else {
        this.search = true;
      }
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
