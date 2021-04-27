import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const prefix = baseURL + "themes";

const settingsURLs = {
  allThemes: `${baseURL}themes`,
  specificTheme: themeName => `${prefix}/${themeName}`,
  createTheme: `${prefix}/create`,
  updateTheme: themeName => `${prefix}/${themeName}`,
  deleteTheme: themeName => `${prefix}/${themeName}`,
};

export const themeAPI = {
  async requestAll() {
    let response = await apiReq.get(settingsURLs.allThemes);
    return response.data;
  },

  async requestByName(name) {
    let response = await apiReq.get(settingsURLs.specificTheme(name));
    return response.data;
  },

  async create(postBody) {
    return await apiReq.post(settingsURLs.createTheme, postBody);
  },

  async update(themeName, colors) {
    const body = {
      name: themeName,
      colors: colors,
    };
    return await apiReq.put(settingsURLs.updateTheme(themeName), body);
  },

  async delete(themeName) {
    return await apiReq.delete(settingsURLs.deleteTheme(themeName));
  },
};
