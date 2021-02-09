const baseURL = "/api/";
import axios from "axios";
import { vueApp } from "../main";

// look for data.snackbar in response
function processResponse(response) {
  try {
    vueApp.flashMessage.show({
      status: response.data.snackbar.type,
      title: 'Error Message Title',
      message: response.data.snackbar.text
    });
  } catch (err) {
    return;
  }


  return;
}

const apiReq = {
  post: async function(url, data) {
    let response = await axios.post(url, data).catch(function(error) {
      if (error.response) {
        processResponse(error.response);
        return error.response;
      }
    });
    processResponse(response);
    return response;
  },

  put: async function(url, data) {
    let response = await axios.put(url, data).catch(function(error) {
      if (error.response) {
        processResponse(error.response);
        return response;
      } else return;
    });
    // processResponse(response);
    return response;
  },

  get: async function(url, data) {
    let response = await axios.get(url, data).catch(function(error) {
      if (error.response) {
        processResponse(error.response);
        return response;
      } else return;
    });
    // processResponse(response);
    return response;
  },

  delete: async function(url, data) {
    let response = await axios.delete(url, data).catch(function(error) {
      if (error.response) {
        processResponse(error.response);
        return response;
      }
    });
    processResponse(response);
    return response;
  },
};

export { apiReq };
export { baseURL };
