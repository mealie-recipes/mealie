<template>
  <div>
    <v-app-bar
      v-if="!isMobile"
      clipped-left
      dense
      app
      color="primary"
      dark
      class="d-print-none"
    >
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

      <TheSiteMenu />
    </v-app-bar>
    <v-app-bar
      v-else
      bottom
      clipped-left
      dense
      app
      color="primary"
      dark
      class="d-print-none"
    >
      <router-link to="/">
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
        <SearchDialog ref="mainSearchDialog" />
      </v-expand-x-transition>
      <v-btn icon @click="$refs.mainSearchDialog.open()">
        <v-icon>mdi-magnify</v-icon>
      </v-btn>

      <TheSiteMenu />
    </v-app-bar>
  </div>
</template>

<script>
import TheSiteMenu from "@/components/UI/TheSiteMenu";
import SearchBar from "@/components/UI/Search/SearchBar";
import SearchDialog from "@/components/UI/Search/SearchDialog";
import { user } from "@/mixins/user";
export default {
  name: "AppBar",

  mixins: [user],
  components: {
    TheSiteMenu,
    SearchBar,
    SearchDialog,
  },
  data() {
    return {
      search: false,
      isMobile: false,
    };
  },
  watch: {
    $route() {
      this.search = false;
    },
  },
  computed: {
    // isMobile() {
    //   return this.$vuetify.breakpoint.name === "xs";
    // },
  },
  methods: {
    navigateFromSearch(slug) {
      this.$router.push(`/recipe/${slug}`);
    },
  },
};
</script>

<style lang="scss" scoped>
</style>