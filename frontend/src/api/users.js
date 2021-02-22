import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
const authPrefix = baseURL + "auth/";

const authURLs = {
  token: `${authPrefix}token`,
};

// const usersURLs = {

// }

export default {
  async login(formData) {
    let response =  await apiReq.post(authURLs.token, formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    console.log(response);
    return response.data;
  },
};
