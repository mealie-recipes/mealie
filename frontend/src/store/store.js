import Vue from "vue";
import Vuex from "vuex";
import api from "../api";
import Vuetify from "../plugins/vuetify";

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    // Snackbar
    snackActive: false,
    snackText: "",
    snackType: "warning",

    // All Recipe Data Store
    recentRecipes: [],
    allRecipes: [],

    // Site Settings
    darkMode: 'system',
    activeTheme: {
      name: 'default',
      colors: {
        primary: "#E58325",
        accent: "#00457A",
        secondary: "#973542",
        success: "#5AB1BB",
        info: "#4990BA",
        warning: "#FF4081",
        error: "#EF5350",
      }
    },
    themes: {
      light: {
        primary: "#E58325",
        accent: "#00457A",
        secondary: "#973542",
        success: "#5AB1BB",
        info: "#4990BA",
        warning: "#FF4081",
        error: "#EF5350",
      },
      dark: {
        primary: "#E58325",
        accent: "#00457A",
        secondary: "#973542",
        success: "#5AB1BB",
        info: "#4990BA",
        warning: "#FF4081",
        error: "#EF5350",
      },
    },
  },

  mutations: {
    setSnackBar(state, payload) {
      state.snackText = payload.text;
      state.snackType = payload.type;
      state.snackActive = true;
    },
    setSnackActive(state, payload) {
      state.snackActive = payload;
    },

    setRecentRecipes(state, payload) {
      state.recentRecipes = payload;
    },

    setDarkMode(state, payload) {
      let isDark;
      state.darkMode = payload;
      Vue.$cookies.set("darkMode", payload);


      if (payload === 'system') {
        //Get System Preference from browser
        const darkMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        isDark = darkMediaQuery.matches;
      }
      else if (payload === 'dark')
        isDark = true;
      else
        isDark = false;

      Vuetify.framework.theme.dark = isDark;
    },

    setActiveTheme(state, payload) {
      state.activeTheme = payload;
      Vue.$cookies.set("activeTheme", payload);

      const themes = payload ? { dark: payload.colors, light: payload.colors } : null
      console.log("themes", themes)
      state.themes = themes;
      Vue.$cookies.set("themes", themes);
      Vuetify.framework.theme.themes = themes;
    },
  },

  actions: {
    async initCookies() {
      //TODO if has no value set to default.
      if (!Vue.$cookies.isKey("themes") || !Vue.$cookies.isKey("activeTheme")) {
        const DEFAULT_THEME = await api.themes.requestByName("default");
        Vue.$cookies.set("themes", {
          light: DEFAULT_THEME.colors,
          dark: DEFAULT_THEME.colors,
        });
        Vue.$cookies.set("activeTheme", {
          name: DEFAULT_THEME.name,
          colors: DEFAULT_THEME.colors
        });
      }

      this.commit("setActiveTheme", Vue.$cookies.get("activeTheme"));

      //https://csabaszabo.dev/blog/dark-mode-for-website-with-nuxtjs-and-vuetify/
      //https://github.com/settings/appearance


      // Dark Mode
      if (!Vue.$cookies.isKey("darkMode")) {
        Vue.$cookies.set("darkMode", 'system');
      }
      this.commit("setDarkMode", Vue.$cookies.get("darkMode"));
    },

    async requestRecentRecipes() {
      const keys = [
        "name",
        "slug",
        "image",
        "description",
        "dateAdded",
        "rating",
      ];
      const payload = await api.recipes.allByKeys(keys);

      this.commit("setRecentRecipes", payload);
    },
  },

  getters: {
    //
    getSnackText: (state) => state.snackText,
    getSnackActive: (state) => state.snackActive,
    getSnackType: (state) => state.snackType,

    getRecentRecipes: (state) => state.recentRecipes,

    // Site Settings
    getDarkMode: (state) => state.darkMode,
    getThemes: (state) => state.themes,
    getActiveTheme: (state) => state.activeTheme
  },
});

export default store;
export { store };
