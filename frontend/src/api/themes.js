import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const themesBase = baseURL + "site-settings/";

const settingsURLs = {
  allThemes: `${themesBase}themes/`,
  specificTheme: (themeName) => `${themesBase}themes/${themeName}/`,
  createTheme: `${themesBase}themes/create/`,
  updateTheme: (themeName) => `${themesBase}themes/${themeName}/update/`,
  deleteTheme: (themeName) => `${themesBase}themes/${themeName}/delete/`,
};

export default {
  async requestAll() {
    let response = await apiReq.get(settingsURLs.allThemes);
    return response.data;
  },

  async requestByName(name) {
    let response = await apiReq.get(settingsURLs.specificTheme(name));
    return response.data;
  },

  async create(postBody) {
    let response = await apiReq.post(settingsURLs.createTheme, postBody);
    return response.data;
  },

  async update(themeName, colors) {
    const body = {
      name: themeName,
      colors: colors,
    };
    let response = await apiReq.post(settingsURLs.updateTheme(themeName), body);
    return response.data;
  },

  async delete(themeName) {
    let response = await apiReq.delete(settingsURLs.deleteTheme(themeName));
    return response.data;
  },
};
