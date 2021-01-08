
import api from "../../api";
import Vuetify from "../../plugins/vuetify";

const state = {
  activeTheme: {},
  darkMode: 'system'

};

const mutations = {
  setTheme(state, payload) {
    Vuetify.framework.theme.themes.dark = payload.colors;
    Vuetify.framework.theme.themes.light = payload.colors;
    state.activeTheme = payload;
  },
  setDarkMode(state, payload) {
    let isDark;

    if (payload === 'system') {
      //Get System Preference from browser
      const darkMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      isDark = darkMediaQuery.matches;
    }
    else if (payload === 'dark')
      isDark = true;
    else if (payload === 'light')
      isDark = false;

    if (isDark !== null) {
      Vuetify.framework.theme.dark = isDark;
      state.darkMode = payload;
    }
  },
};

const actions = {
  async resetTheme({ commit }) {
    const defaultTheme = await api.themes.requestByName("default");
    if (defaultTheme.colors) {
      Vuetify.framework.theme.themes.dark = defaultTheme.colors;
      Vuetify.framework.theme.themes.light = defaultTheme.colors;
      commit('setTheme', defaultTheme)
    }
  },

  async initTheme({ dispatch, getters }) {
    //If theme is empty resetTheme
    if (Object.keys(getters.getActiveTheme).length === 0) {
      await dispatch('resetTheme')
    }
    else {
      Vuetify.framework.theme.themes.dark = getters.getActiveTheme.colors;
      Vuetify.framework.theme.themes.light = getters.getActiveTheme.colors;
    }
  },

}

const getters = {
  getActiveTheme: (state) => state.activeTheme,
  getDarkMode: (state) => state.darkMode
}

export default {
  state,
  mutations,
  actions,
  getters
}