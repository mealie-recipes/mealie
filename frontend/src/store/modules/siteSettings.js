import { api } from "@/api";
import { loadLanguageAsync } from "@/i18n"

const state = {
  siteSettings: {
    language: "en-US",
    firstDayOfWeek: 0,
    showRecent: true,
    cardsPerSection: 9,
    categories: [],
  },
  customPages: [],
};

const mutations = {
  setSettings(state, payload) {
    state.siteSettings = payload;
    loadLanguageAsync(payload.language);
  },
  setCustomPages(state, payload) {
    state.customPages = payload;
  },
};

const actions = {
  async requestSiteSettings({ commit }) {
    let settings = await api.siteSettings.get();
    commit("setSettings", settings);
  },
  async requestCustomPages({ commit }) {
    const customPages = await api.siteSettings.getPages();
    commit("setCustomPages", customPages);
  },
};

const getters = {
  getActiveLang: state => state.siteSettings.language,
  getSiteSettings: state => state.siteSettings,
  getCustomPages: state => state.customPages,
};

export default {
  state,
  mutations,
  actions,
  getters,
};
