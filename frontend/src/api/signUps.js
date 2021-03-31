import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const signUpPrefix = baseURL + "users/sign-ups";

const signUpURLs = {
  all: `${signUpPrefix}`,
  createToken: `${signUpPrefix}`,
  deleteToken: token => `${signUpPrefix}/${token}`,
  createUser: token => `${signUpPrefix}/${token}`,
};

export const signupAPI = {
  async getAll() {
    let response = await apiReq.get(signUpURLs.all);
    return response.data;
  },
  async createToken(data) {
    let response = await apiReq.post(signUpURLs.createToken, data);
    return response.data;
  },
  async deleteToken(token) {
    let response = await apiReq.delete(signUpURLs.deleteToken(token));
    return response.data;
  },
  async createUser(token, data) {
    let response = await apiReq.post(signUpURLs.createUser(token), data);
    return response.data;
  },
};
