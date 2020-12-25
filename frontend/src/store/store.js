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
    darkMode: false,
    themes: {
      light: {
        primary: "#E58325",
        accent: "#00457A",
        secondary: "#973542",
        success: "#43A047",
        info: "#FFFD99",
        warning: "#FF4081",
        error: "#EF5350",
      },
      dark: {
        primary: "#4527A0",
        accent: "#FF4081",
        secondary: "#26C6DA",
        success: "#43A047",
        info: "#2196F3",
        warning: "#FB8C00",
        error: "#FF5252",
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
      state.darkMode = payload;
      Vue.$cookies.set("darkMode", payload);
      Vuetify.framework.theme.dark = payload;
    },

    setThemes(state, payload) {
      state.themes = payload;
      Vue.$cookies.set("themes", payload);
      Vuetify.framework.theme.themes = payload;
    },
  },

  actions: {
    async initCookies() {
      if (!Vue.$cookies.isKey("themes")) {
        const DEFAULT_THEME = await api.themes.requestByName("default");
        Vue.$cookies.set("themes", {
          light: DEFAULT_THEME.colors,
          dark: DEFAULT_THEME.colors,
        });
      }

      this.commit("setThemes", Vue.$cookies.get("themes"));

      // Dark Mode
      if (!Vue.$cookies.isKey("darkMode")) {
        Vue.$cookies.set("darkMode", false);
      }
      this.commit("setDarkMode", JSON.parse(Vue.$cookies.get("darkMode")));
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
  },
});

export default store;
export { store };
