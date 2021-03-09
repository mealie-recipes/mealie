import api from "@/api";

const state = {
  siteSettings: {
    language: "en",
    showRecent: true,
    cardsPerSection: 9,
    categories: [],
  },
};

const mutations = {
  setSettings(state, payload) {
    state.settings = payload;
  },
};

const actions = {
  async requestSiteSettings() {
    let settings = await api.siteSettings.get();
    this.commit("setSettings", settings);
  },
};

const getters = {
  getSiteSettings: state => state.siteSettings,
};

export default {
  state,
  mutations,
  actions,
  getters,
};
