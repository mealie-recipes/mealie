import Vue from "vue";
import Vuex from "vuex";
import api from "@/api";
import createPersistedState from "vuex-persistedstate";
import userSettings from "./modules/userSettings";
import language from "./modules/language";
import homePage from "./modules/homePage";
import siteSettings from "./modules/siteSettings";

Vue.use(Vuex);

const store = new Vuex.Store({
  plugins: [
    createPersistedState({
      paths: ["userSettings", "language", "homePage", "SideSettings"],
    }),
  ],
  modules: {
    userSettings,
    language,
    homePage,
    siteSettings,
  },
  state: {
    // All Recipe Data Store
    recentRecipes: [],
    allRecipes: [],
    mealPlanCategories: [],
  },

  mutations: {
    setRecentRecipes(state, payload) {
      state.recentRecipes = payload;
    },

    setMealPlanCategories(state, payload) {
      state.mealPlanCategories = payload;
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
  },

  getters: {
    getRecentRecipes: state => state.recentRecipes,
    getMealPlanCategories: state => state.mealPlanCategories,
  },
});

export default store;
export { store };
