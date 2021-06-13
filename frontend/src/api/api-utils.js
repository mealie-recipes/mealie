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

const requests = {
  /**
   *
   * @param {*} funcCall Callable Axios Function
   * @param {*} url Destination url
   * @param {*} data Request Data
   * @param {*} getErrorText Error Text Function
   * @param {*} getSuccessText Success Text Function
   * @returns Object response
   */
  unsafe: async function(funcCall, url, data, getErrorText = defaultErrorText, getSuccessText) {
    const response = await funcCall(url, data).catch(function(error) {
      handleError(error, getErrorText);
    });
    return handleResponse(response, getSuccessText);
  },
  /**
   *
   * @param {*} funcCall Callable Axios Function
   * @param {*} url Destination url
   * @param {*} data Request Data
   * @param {*} getErrorText Error Text Function
   * @param {*} getSuccessText Success Text Function
   * @returns Array [response, error]
   */
  safe: async function(funcCall, url, data, getErrorText = defaultErrorText, getSuccessText) {
    const response = await funcCall(url, data).catch(function(error) {
      handleError(error, getErrorText);
      return [null, error];
    });
    return [handleResponse(response, getSuccessText), null];
  },
};

const apiReq = {
  get: async function(url, getErrorText = defaultErrorText) {
    return axios.get(url).catch(function(error) {
      handleError(error, getErrorText);
    });
  },

  getSafe: async function(url) {
    let error = null;
    const response = await axios.get(url).catch(e => {
      error = e;
    });
    return [response, error];
  },

  post: async function(url, data, getErrorText = defaultErrorText, getSuccessText) {
    return await requests.unsafe(axios.post, url, data, getErrorText, getSuccessText);
  },

  postSafe: async function(url, data, getErrorText = defaultErrorText, getSuccessText) {
    return await requests.safe(axios.post, url, data, getErrorText, getSuccessText);
  },

  put: async function(url, data, getErrorText = defaultErrorText, getSuccessText) {
    return await requests.unsafe(axios.put, url, data, getErrorText, getSuccessText);
  },

  putSafe: async function(url, data, getErrorText = defaultErrorText, getSuccessText) {
    return await requests.safe(axios.put, url, data, getErrorText, getSuccessText);
  },

  patch: async function(url, data, getErrorText = defaultErrorText, getSuccessText) {
    return await requests.unsafe(axios.patch, url, data, getErrorText, getSuccessText);
  },

  patchSafe: async function(url, data, getErrorText = defaultErrorText, getSuccessText) {
    return await requests.safe(axios.patch, url, data, getErrorText, getSuccessText);
  },

  delete: async function(url, data, getErrorText = defaultErrorText, getSuccessText = defaultSuccessText) {
    return await requests.unsafe(axios.delete, url, data, getErrorText, getSuccessText);
  },

  deleteSafe: async function(url, data, getErrorText = defaultErrorText, getSuccessText = defaultSuccessText) {
    return await requests.unsafe(axios.delete, url, data, getErrorText, getSuccessText);
  },

  download: async function(url) {
    const response = await this.get(url);
    const token = response.data.fileToken;

    const tokenURL = prefix + "utils/download?token=" + token;
    window.open(tokenURL, "_blank");
    return response.data;
  },
};

export { apiReq };
