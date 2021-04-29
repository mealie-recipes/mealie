import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import i18n from '@/i18n.js';

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
    let response = await apiReq.post(
      signUpURLs.createToken, 
      data,
      function() { return i18n.t('signup.sign-up-link-creation-failed'); },
      function() { return i18n.t('signup.sign-up-link-created'); }
    );
    return response.data;
  },
  async deleteToken(token) {
    return await apiReq.delete(signUpURLs.deleteToken(token),
    null,
    function() { return i18n.t('signup.sign-up-token-deletion-failed'); },
    function() { return i18n.t('signup.sign-up-token-deleted'); }
    );
  },
  async createUser(token, data) {
    return apiReq.post(signUpURLs.createUser(token), data,
    function() { return i18n.t('user.you-are-not-allowed-to-create-a-user'); },
    function() { return i18n.t('user.user-created'); }
    );
  },
};
