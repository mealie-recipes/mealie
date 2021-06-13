import { prefix } from "./apiRoutes";
import axios from "axios";
import { store } from "../store";
import { utils } from "@/utils";

axios.defaults.headers.common["Authorization"] = `Bearer ${store.getters.getToken}`;

function handleError(error, getText) {
  if (getText) {
    utils.notify.error(getText(error.response));
  }
  return false;
}
function handleResponse(response, getText) {
  if (response && getText) {
    const successText = getText(response);
    utils.notify.success(successText);
  }
  return response;
}

function defaultErrorText(response) {
  return response.statusText;
}

function defaultSuccessText(response) {
  return response.statusText;
}

const apiReq = {
  post: async function(url, data, getErrorText = defaultErrorText, getSuccessText) {
    const response = await axios.post(url, data).catch(function(error) {
      handleError(error, getErrorText);
      return error;
    });
    return handleResponse(response, getSuccessText);
  },

  put: async function(url, data, getErrorText = defaultErrorText, getSuccessText) {
    const response = await axios.put(url, data).catch(function(error) {
      handleError(error, getErrorText);
      return error;
    });
    return handleResponse(response, getSuccessText);
  },

  patch: async function(url, data, getErrorText = defaultErrorText, getSuccessText) {
    const response = await axios.patch(url, data).catch(function(error) {
      handleError(error, getErrorText);
      return error;
    });
    return handleResponse(response, getSuccessText);
  },

  get: async function(url, data, getErrorText = defaultErrorText) {
    return axios.get(url, data).catch(function(error) {
      handleError(error, getErrorText);
      return error;
    });
  },

  delete: async function(url, data, getErrorText = defaultErrorText, getSuccessText = defaultSuccessText) {
    const response = await axios.delete(url, data).catch(function(error) {
      handleError(error, getErrorText);
      return error;
    });
    return handleResponse(response, getSuccessText);
  },

  async download(url) {
    const response = await this.get(url);
    const token = response.data.fileToken;

    const tokenURL = prefix + "utils/download?token=" + token;
    window.open(tokenURL, "_blank");
    return response.data;
  },
};

export { apiReq };
