import { apiReq } from "./api-utils";
import i18n from "@/i18n.js";
import { API_ROUTES } from "./apiRoutes";

export const signupAPI = {
  async getAll() {
    let response = await apiReq.get(API_ROUTES.usersSignUps);
    return response.data;
  },
  async createToken(data) {
    let response = await apiReq.post(
      API_ROUTES.usersSignUps,
      data,
      () => i18n.t("signup.sign-up-link-creation-failed"),
      () => i18n.t("signup.sign-up-link-created")
    );
    return response.data;
  },
  async deleteToken(token) {
    return await apiReq.delete(
      API_ROUTES.usersSignUpsToken(token),
      null,
      () => i18n.t("signup.sign-up-token-deletion-failed"),
      () => i18n.t("signup.sign-up-token-deleted")
    );
  },
  async createUser(token, data) {
    return apiReq.post(
      API_ROUTES.usersSignUpsToken(token),
      data,
      () => i18n.t("user.you-are-not-allowed-to-create-a-user"),
      () => i18n.t("user.user-created")
    );
  },
};
