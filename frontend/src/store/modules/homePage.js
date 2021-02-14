import api from "@/api";

const state = {
  showRecent: true,
  showLimit: 9,
  categories: [],
  homeCategories: [],
};

const mutations = {
  setShowRecent(state, payload) {
    state.showRecent = payload;
  },
  setShowLimit(state, payload) {
    state.showLimit = payload;
  },
  setCategories(state, payload) {
    state.categories = payload.sort((a, b) => (a.name > b.name ? 1 : -1));
  },
  setHomeCategories(state, payload) {
    state.homeCategories = payload;
  },
};

const actions = {
  async requestHomePageSettings() {
    let categories = await api.categories.get_all();
    this.commit("setCategories", categories);
  },
};

const getters = {
  getShowRecent: state => state.showRecent,
  getShowLimit: state => state.showLimit,
  getCategories: state => state.categories,
  getHomeCategories: state => state.homeCategories,
};

export default {
  state,
  mutations,
  actions,
  getters,
};
