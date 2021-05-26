import { api } from "@/api";
import Vue from "vue";
import { recipe } from "@/utils/recipe";

const state = {
  recentRecipes: [],
  allRecipes: [],
};

const mutations = {
  setRecentRecipes(state, payload) {
    state.recentRecipes = payload;
  },
  patchRecentRecipes(state, payload) {
    if (state.recentRecipes[payload.id]) {
      state.recentRecipes[payload.id] = payload;
    }
  },
  dropRecentRecipes(state, payload) {
    if (state.recentRecipes[payload.id]) {
      Vue.delete(state.recentRecipes, payload.id);
    }
  },
  setAllRecipes(state, payload) {
    state.allRecipes = payload;
  },
  patchAllRecipes(state, payload) {
    state.allRecipes[payload.id] = payload;
  },
  dropAllRecipes(state, payload) {
    if (state.allRecipes[payload.id]) {
      Vue.delete(state.allRecipes, payload.id);
    }
  },
};

const actions = {
  async requestRecentRecipes() {
    const payload = await api.recipes.allSummary(0, 30);
    const hash = Object.fromEntries(payload.map(e => [e.id, e]));
    this.commit("setRecentRecipes", hash);
  },
  async requestAllRecipes({ getters }) {
    console.log("All Recipes");
    const all = getters.getAllRecipes;
    const payload = await api.recipes.allSummary(all.length, 9999);
    const hash = Object.fromEntries([...all, ...payload].map(e => [e.id, e]));

    this.commit("setAllRecipes", hash);
  },
  patchRecipe({ commit }, payload) {
    commit("patchAllRecipes", payload);
    commit("patchRecentRecipes", payload);
  },
  dropRecipe({ commit }, payload) {
    commit("dropAllRecipes", payload);
    commit("dropRecentRecipes", payload);
  },
};

const getters = {
  getAllRecipes: state => Object.values(state.allRecipes),
  getAllRecipesHash: state => state.allRecipes,
  getRecentRecipes: state => {
    let list = Object.values(state.recentRecipes);
    recipe.sortByUpdated(list);
    return list;
  },
  getRecentRecipesHash: state => state.recentRecipes,
};

export default {
  state,
  mutations,
  actions,
  getters,
};
