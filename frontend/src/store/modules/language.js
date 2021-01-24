import VueI18n from "../../i18n";

const state = {
  lang: "en",
  allLangs: [
    {
      name: "English",
      value: "en",
    },
    {
      name: "Dutch",
      value: "da",
    },
    {
      name: "French",
      value: "fr",
    },
  ],
};

const mutations = {
  setLang(state, payload) {
    VueI18n.locale = payload;
    state.lang = payload;
  },
};

const actions = {
  initLang({ getters }) {
    VueI18n.locale = getters.getActiveLang;
  },
};

const getters = {
  getActiveLang: (state) => state.lang,
  getAllLangs: (state) => state.allLangs,
};

export default {
  state,
  mutations,
  actions,
  getters,
};
