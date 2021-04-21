import VueI18n from "../../i18n";

const state = {
  lang: "en-US",
  allLangs: [
    {
      name: "English",
      value: "en-US",
    },
    {
      name: "Danish",
      value: "da-DK",
    },
    {
      name: "French",
      value: "fr-FR",
    },
    {
      name: "Polish",
      value: "pl-PL",
    },
    {
      name: "Swedish",
      value: "sv-SE",
    },
    {
      name: "简体中文",
      value: "zh-CN",
    },
    {
      name: "繁體中文",
      value: "zh-TW",
    },
    {
      name: "German",
      value: "de-DE",
    },
    {
      name: "Português",
      value: "pt-PT",
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
  initLang({ getters }, { currentVueComponent }) {
    VueI18n.locale = getters.getActiveLang;
    currentVueComponent.$vuetify.lang.current = getters.getActiveLang;
  },
  setLang({ commit }, { language, currentVueComponent }) {
    VueI18n.locale = language;
    currentVueComponent.$vuetify.lang.current = language;
    commit('setLang', language);
  },
};

const getters = {
  getActiveLang: state => state.lang,
  getAllLangs: state => state.allLangs,
};

export default {
  state,
  mutations,
  actions,
  getters,
};
