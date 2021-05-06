import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import axios from "axios";
import i18n from "@/i18n.js";
const authPrefix = baseURL + "auth";
const userPrefix = baseURL + "users";

const authURLs = {
  token: `${authPrefix}/token`,
  refresh: `${authPrefix}/refresh`,
};

const usersURLs = {
  users: `${userPrefix}`,
  self: `${userPrefix}/self`,
  userID: id => `${userPrefix}/${id}`,
  password: id => `${userPrefix}/${id}/password`,
  resetPassword: id => `${userPrefix}/${id}/reset-password`,
  userAPICreate: `${userPrefix}/api-tokens`,
  userAPIDelete: id => `${userPrefix}/api-tokens/${id}`,
};

export const userAPI = {
  async login(formData) {
    let response = await apiReq.post(authURLs.token, formData, null, function() {
      return i18n.t("user.user-successfully-logged-in");
    });
    return response;
  },
  async refresh() {
    let response = await axios.get(authURLs.refresh).catch(function(event) {
      console.log("Fetch failed", event);
    });
    return response.data ? response.data : false;
  },
  async allUsers() {
    let response = await apiReq.get(usersURLs.users);
    return response.data;
  },
  create(user) {
    return apiReq.post(
      usersURLs.users,
      user,
      () => i18n.t("user.user-creation-failed"),
      () => i18n.t("user.user-created")
    );
  },
  async self() {
    let response = await apiReq.get(usersURLs.self);
    return response.data;
  },
  async byID(id) {
    let response = await apiReq.get(usersURLs.userID(id));
    return response.data;
  },
  update(user) {
    return apiReq.put(
      usersURLs.userID(user.id),
      user,
      () => i18n.t("user.user-update-failed"),
      () => i18n.t("user.user-updated")
    );
  },
  changePassword(id, password) {
    return apiReq.put(
      usersURLs.password(id),
      password,
      () => i18n.t("user.existing-password-does-not-match"),
      () => i18n.t("user.password-updated")
    );
  },

  delete(id) {
    return apiReq.delete(usersURLs.userID(id), null, deleteErrorText, function() {
      return i18n.t("user.user-deleted");
    });
  },
  resetPassword(id) {
    return apiReq.put(
      usersURLs.resetPassword(id),
      null,
      () => i18n.t("user.password-reset-failed"),
      () => i18n.t("user.password-has-been-reset-to-the-default-password")
    );
  },
  async createAPIToken(name) {
    const response = await apiReq.post(usersURLs.userAPICreate, { name });
    return response.data;
  },
  async deleteAPIToken(id) {
    const response = await apiReq.delete(usersURLs.userAPIDelete(id));
    return response.data;
  },
};

const deleteErrorText = response => {
  switch (response.data.detail) {
    case "SUPER_USER":
      return i18n.t("user.error-cannot-delete-super-user");
    default:
      return i18n.t("user.you-are-not-allowed-to-delete-this-user");
  }
};
