const baseURL = "/api/";
import axios from "axios";
import store from "../store/store";

function processResponse(response) {
  if (("data" in response) & ("snackbar" in response.data)) {
    store.commit("setSnackBar", {
      text: response.data.snackbar.text,
      type: response.data.snackbar.type,
    });
  } else return;
}

const apiReq = {
  post: async function(url, data) {
    let response = await axios.post(url, data).catch(function(error) {
      if (error.response) {
        console.log("Error");
        processResponse(error.response);
        return;
      }
    });
    processResponse(response);
    return response;
  },

  get: async function(url, data) {
    let response = await axios.get(url, data).catch(function(error) {
      if (error.response) {
        processResponse(error.response);
        return;
      } else return;
    });
    // processResponse(response);
    return response;
  },

  delete: async function(url, data) {
    let response = await axios.delete(url, data).catch(function(error) {
      if (error.response) {
        processResponse(error.response);
        return;
      }
    });
    processResponse(response);
    return response;
  },
};

export { apiReq };
export { baseURL };
