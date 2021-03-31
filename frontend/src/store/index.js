import Vue from "vue";
import Vuex from "vuex";
import { api } from "@/api";
import createPersistedState from "vuex-persistedstate";
import userSettings from "./modules/userSettings";
import language from "./modules/language";
import siteSettings from "./modules/siteSettings";
import groups from "./modules/groups";

Vue.use(Vuex);

const store = new Vuex.Store({
  plugins: [
    createPersistedState({
      paths: ["userSettings", "language", "SideSettings"],
    }),
  ],
  modules: {
    userSettings,
    language,
    siteSettings,
    groups,
  },
  state: {
    // All Recipe Data Store
    recentRecipes: [],
    allRecipes: [],
    mealPlanCategories: [],
    allCategories: [],
    allTags: [],
  },

  mutations: {
    setRecentRecipes(state, payload) {
      state.recentRecipes = payload;
    },
    setMealPlanCategories(state, payload) {
      state.mealPlanCategories = payload;
    },
    setAllCategories(state, payload) {
      state.allCategories = payload;
    },
    setAllTags(state, payload) {
      state.allTags = payload;
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
    async requestCategories({ commit }) {
      const categories = await api.categories.getAll();
      commit("setAllCategories", categories);
    },
    async requestTags({ commit }) {
      const tags = await api.tags.getAll();
      commit("setAllTags", tags);
    },
  },

  getters: {
    getRecentRecipes: state => state.recentRecipes,
    getMealPlanCategories: state => state.mealPlanCategories,
    getAllCategories: state =>
      state.allCategories.sort((a, b) => (a.slug > b.slug ? 1 : -1)),
    getAllTags: state =>
      state.allTags.sort((a, b) => (a.slug > b.slug ? 1 : -1)),
  },
});

export default store;
export { store };
