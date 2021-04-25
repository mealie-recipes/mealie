<template>
  <div>
    <TheSidebar ref="theSidebar" />
    <v-app-bar
      clipped-left
      dense
      app
      color="primary"
      dark
      class="d-print-none"
      :bottom="isMobile"
    >
      <v-btn icon @click="openSidebar">
        <v-icon> mdi-menu </v-icon>
      </v-btn>
      <router-link to="/">
        <v-btn icon>
          <v-icon size="40"> mdi-silverware-variant </v-icon>
        </v-btn>
      </router-link>

      <div v-if="!isMobile" btn class="pl-2">
        <v-toolbar-title style="cursor: pointer" @click="$router.push('/')">
          Mealie
        </v-toolbar-title>
      </div>

      <v-spacer></v-spacer>
      <SearchBar
        v-if="!isMobile"
        :show-results="true"
        @selected="navigateFromSearch"
        :max-width="isMobile ? '100%' : '450px'"
      />
      <div v-else>
        <v-btn icon @click="$refs.recipeSearch.open()">
          <v-icon> mdi-magnify </v-icon>
        </v-btn>
        <SearchDialog ref="recipeSearch"/>
      </div>

      <TheSiteMenu />

      <v-slide-x-reverse-transition>
        <TheRecipeFab v-if="loggedIn && isMobile" />
      </v-slide-x-reverse-transition>
    </v-app-bar>
    <v-slide-x-reverse-transition>
      <TheRecipeFab v-if="loggedIn && !isMobile" :absolute="true" />
    </v-slide-x-reverse-transition>
  </div>
</template>

<script>
import TheSiteMenu from "@/components/UI/TheSiteMenu";
import SearchBar from "@/components/UI/Search/SearchBar";
import SearchDialog from "@/components/UI/Search/SearchDialog";
import TheRecipeFab from "@/components/UI/TheRecipeFab";
import TheSidebar from "@/components/UI/TheSidebar";
import { user } from "@/mixins/user";
export default {
  name: "AppBar",

  mixins: [user],
  components: {
    SearchDialog,
    TheRecipeFab,
    TheSidebar,
    TheSiteMenu,
    SearchBar,
  },
  data() {
    return {
      showSidebar: false,
    };
  },
  computed: {
    isMobile() {
      return this.$vuetify.breakpoint.name === "xs";
    },
  },
  methods: {
    navigateFromSearch(slug) {
      this.$router.push(`/recipe/${slug}`);
    },
    openSidebar() {
      this.$refs.theSidebar.toggleSidebar();
    },
  },
};
</script>

<style scoped>
</style>