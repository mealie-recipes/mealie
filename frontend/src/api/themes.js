import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const prefix = baseURL + "themes/";

const settingsURLs = {
  allThemes: `${baseURL}themes`,
  specificTheme: (themeName) => `${prefix}themes/${themeName}`,
  createTheme: `${prefix}themes/create`,
  updateTheme: (themeName) => `${prefix}themes/${themeName}`,
  deleteTheme: (themeName) => `${prefix}themes/${themeName}`,
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
    let response = await apiReq.put(settingsURLs.updateTheme(themeName), body);
    return response.data;
  },

  async delete(themeName) {
    let response = await apiReq.delete(settingsURLs.deleteTheme(themeName));
    return response.data;
  },
};
