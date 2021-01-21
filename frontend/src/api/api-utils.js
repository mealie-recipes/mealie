const baseURL = "/api/";
import axios from "axios";
import store from "../store/store";

// look for data.snackbar in response
function processResponse(response) {
  try {
    store.commit("setSnackBar", {
      text: response.data.snackbar.text,
      type: response.data.snackbar.type,
    });
  } catch (err) {
    return;
  }
  return;
}

const apiReq = {
  post: async function (url, data) {
    let response = await axios.post(url, data).catch(function (error) {
      if (error.response) {
        processResponse(error.response);
        return error.response;
      }
    });
    processResponse(response);
    return response;
  },

  get: async function (url, data) {
    let response = await axios.get(url, data).catch(function (error) {
      if (error.response) {
        processResponse(error.response);
        return response;
      } else return;
    });
    // processResponse(response);
    return response;
  },

  delete: async function (url, data) {
    let response = await axios.delete(url, data).catch(function (error) {
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
