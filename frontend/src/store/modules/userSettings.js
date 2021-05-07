import { api } from "@/api";
import Vuetify from "@/plugins/vuetify";
import axios from "axios";

function inDarkMode(payload) {
  let isDark;

  if (payload === "system") {
    //Get System Preference from browser
    const darkMediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    isDark = darkMediaQuery.matches;
  } else if (payload === "dark") isDark = true;
  else if (payload === "light") isDark = false;

  return isDark;
}

const state = {
  activeTheme: {},
  darkMode: "light",
  isDark: false,
  isLoggedIn: false,
  token: "",
  userData: {},
};

const mutations = {
  setTheme(state, payload) {
    Vuetify.framework.theme.themes.dark = payload.colors;
    Vuetify.framework.theme.themes.light = payload.colors;
    state.activeTheme = payload;
  },
  setDarkMode(state, payload) {
    let isDark = inDarkMode(payload);

    if (isDark !== null) {
      Vuetify.framework.theme.dark = isDark;
      state.isDark = isDark;
      state.darkMode = payload;
    }
  },
  setIsLoggedIn(state, payload) {
    state.isLoggedIn = payload;
  },
  setToken(state, payload) {
    state.isLoggedIn = true;
    axios.defaults.headers.common["Authorization"] = `Bearer ${payload}`;
    state.token = payload;
  },

  setUserData(state, payload) {
    state.userData = payload;
  },
};

const actions = {
  async requestUserData({ commit }) {
    const userData = await api.users.self();
    commit("setUserData", userData);
  },

  async resetTheme({ commit }) {
    const defaultTheme = await api.themes.requestByName(1);
    if (defaultTheme.colors) {
      Vuetify.framework.theme.themes.dark = defaultTheme.colors;
      Vuetify.framework.theme.themes.light = defaultTheme.colors;
      commit("setTheme", defaultTheme);
    }
  },

  async refreshToken({ commit, getters }) {
    if (!getters.getIsLoggedIn) {
      commit("setIsLoggedIn", false); // This has to be here... for some reasons?  ¯\_(ツ)_/¯
      console.log("Not Logged In");
      return;
    }
    try {
      let authResponse = await api.users.refresh();
      commit("setToken", authResponse.access_token);
    } catch {
      console.log("Failed Token Refresh, Logging Out...");
      commit("setIsLoggedIn", false);
    }
  },

  async initTheme({ dispatch, getters }) {
    //If theme is empty resetTheme
    if (Object.keys(getters.getActiveTheme).length === 0) {
      await dispatch("resetTheme");
    } else {
      Vuetify.framework.theme.dark = inDarkMode(getters.getDarkMode);
      Vuetify.framework.theme.themes.dark = getters.getActiveTheme.colors;
      Vuetify.framework.theme.themes.light = getters.getActiveTheme.colors;
    }
  },
};

const getters = {
  getActiveTheme: state => state.activeTheme,
  getDarkMode: state => state.darkMode,
  getIsDark: state => state.isDark,
  getIsLoggedIn: state => state.isLoggedIn,
  getToken: state => state.token,
  getUserData: state => state.userData,
};

export default {
  state,
  mutations,
  actions,
  getters,
};
