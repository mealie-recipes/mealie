const baseURL = "/api/";
import axios from "axios";
import { store } from "../store";

axios.defaults.headers.common[
  "Authorization"
] = `Bearer ${store.getters.getToken}`;

const apiReq = {
  post: async function(url, data) {
    let response = await axios.post(url, data).catch(function(error) {
      if (error.response) {
        return error.response;
      }
    });
    return response;
  },

  put: async function(url, data) {
    let response = await axios.put(url, data).catch(function(error) {
      if (error.response) {
        return error.response;
      } else return;
    });
    return response;
  },
  patch: async function(url, data) {
    let response = await axios.patch(url, data).catch(function(error) {
      if (error.response) {
        processResponse(error.response);
        return response;
      } else return;
    });
    processResponse(response);
    return response;
  },

  get: async function(url, data) {
    let response = await axios.get(url, data).catch(function(error) {
      if (error.response) {
        return error.response;
      } else return;
    });
    return response;
  },

  delete: async function(url, data) {
    let response = await axios.delete(url, data).catch(function(error) {
      if (error.response) {
        return error.response;
      }
    });
    return response;
  },

  async download(url) {
    const response = await this.get(url);
    const token = response.data.fileToken;

    const tokenURL = baseURL + "utils/download?token=" + token;
    window.open(tokenURL, "_blank");
    return response.data;
  },
};

export { apiReq };
export { baseURL };
