import Vue from "vue";
import Vuex from "vuex";
import api from "../api";
import createPersistedState from "vuex-persistedstate";
import userSettings from "./modules/userSettings";
import language from "./modules/language";

Vue.use(Vuex);

const store = new Vuex.Store({
  plugins: [
    createPersistedState({
      paths: ["userSettings", "language"],
    }),
  ],
  modules: {
    userSettings,
    language,
  },
  state: {
    // Home Page Settings
    homePageSettings: {
      showRecent: true,
      showLimit: 9,
      categories: [],
      homeCategories: [],
    },
    // Snackbar
    snackActive: false,
    snackText: "",
    snackType: "warning",

    // All Recipe Data Store
    recentRecipes: [],
    allRecipes: [],
  },

  mutations: {
    setHomePageSettings(state, payload) {
      state.homePageSettings = payload;
    },
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
  },

  actions: {
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

    async requestHomePageSettings() {
      // TODO: Query Backend for Categories
      // this.commit("setHomePage", {
      //   showRecent: true,
      //   showLimit: 9,
      //   categories: ["breakfast", "lunch", "dinner"],
      // });
    },
  },

  getters: {
    //
    getSnackText: (state) => state.snackText,
    getSnackActive: (state) => state.snackActive,
    getSnackType: (state) => state.snackType,

    getRecentRecipes: (state) => state.recentRecipes,
    getHomePageSettings: (state) => state.homePageSettings,
  },
});

export default store;
export { store };
