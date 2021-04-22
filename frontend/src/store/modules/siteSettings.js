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
};

const mutations = {
  setSettings(state, payload) {
    state.siteSettings = payload;
    VueI18n.locale = payload.language;
    Vuetify.framework.lang.current = payload.language;
  },
};

const actions = {
  async requestSiteSettings({ commit }) {
    let settings = await api.siteSettings.get();
    commit("setSettings", settings);
  },
};

const getters = {
  getActiveLang: state => state.siteSettings.language,
  getSiteSettings: state => state.siteSettings,
};

export default {
  state,
  mutations,
  actions,
  getters,
};
