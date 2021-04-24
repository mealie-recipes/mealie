import { api } from "@/api";
import VueI18n from "@/i18n";
import Vuetify from "@/plugins/vuetify";

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
    VueI18n.locale = payload.language;
    Vuetify.framework.lang.current = payload.language;
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
  async requestCustomPages({commit }) {
    const customPages = await api.siteSettings.getPages()
    commit("setCustomPages", customPages)
  }
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
