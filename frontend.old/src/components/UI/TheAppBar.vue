<template>
  <div>
    <TheSidebar ref="theSidebar" />
    <v-app-bar clipped-left dense app color="primary" dark class="d-print-none" :bottom="isMobile">
      <v-btn icon @click="openSidebar">
        <v-icon> {{ $globals.icons.menu }}</v-icon>
      </v-btn>
      <router-link to="/">
        <v-btn icon>
          <v-icon size="40"> {{ $globals.icons.primary }} </v-icon>
        </v-btn>
      </router-link>

      <div v-if="!isMobile" btn class="pl-2">
        <v-toolbar-title style="cursor: pointer" @click="$router.push('/')">
          Mealie
        </v-toolbar-title>
      </div>

      <v-spacer></v-spacer>
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon class="mr-1" small v-bind="attrs" v-on="on" @click="isDark = !isDark">
            <v-icon v-text="isDark ? $globals.icons.weatherSunny : $globals.icons.weatherNight"> </v-icon>
          </v-btn>
        </template>
        <span>{{ isDark ? $t("settings.theme.switch-to-light-mode") : $t("settings.theme.switch-to-dark-mode") }}</span>
      </v-tooltip>
      <div v-if="!isMobile" style="width: 350px;">
        <SearchBar :show-results="true" @selected="navigateFromSearch" :max-width="isMobile ? '100%' : '450px'" />
      </div>
      <div v-else>
        <v-btn icon @click="$refs.recipeSearch.open()">
          <v-icon> {{ $globals.icons.search }} </v-icon>
        </v-btn>
        <SearchDialog ref="recipeSearch" />
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
import SearchDialog from "@/components/UI/Dialogs/SearchDialog";
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
    isDark: {
      get() {
        return this.$store.getters.getIsDark;
      },
      set() {
        let setVal = "dark";
        if (this.isDark) {
          setVal = "light";
        }
        this.$store.commit("setDarkMode", setVal);
      },
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

<style scoped></style>
