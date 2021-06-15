import { API_ROUTES } from "./apiRoutes";
import { apiReq } from "./api-utils";
import i18n from "@/i18n.js";

export const userAPI = {
  async login(formData) {
    let response = await apiReq.post(API_ROUTES.authToken, formData, null, () => {
      return i18n.t("user.user-successfully-logged-in");
    });
    return response;
  },
  async refresh() {
    return apiReq.getSafe(API_ROUTES.authRefresh);
  },
  async allUsers() {
    let response = await apiReq.get(API_ROUTES.users);
    return response.data;
  },
  create(user) {
    return apiReq.post(
      API_ROUTES.users,
      user,
      () => i18n.t("user.user-creation-failed"),
      () => i18n.t("user.user-created")
    );
  },
  async self() {
    return apiReq.getSafe(API_ROUTES.usersSelf);
  },
  async byID(id) {
    let response = await apiReq.get(API_ROUTES.usersId(id));
    return response.data;
  },
  update(user) {
    return apiReq.put(
      API_ROUTES.usersId(user.id),
      user,
      () => i18n.t("user.user-update-failed"),
      () => i18n.t("user.user-updated")
    );
  },
  changePassword(id, password) {
    return apiReq.put(
      API_ROUTES.usersIdPassword(id),
      password,
      () => i18n.t("user.existing-password-does-not-match"),
      () => i18n.t("user.password-updated")
    );
  },

  delete(id) {
    return apiReq.delete(API_ROUTES.usersId(id), null, deleteErrorText, () => {
      return i18n.t("user.user-deleted");
    });
  },
  resetPassword(id) {
    return apiReq.put(
      API_ROUTES.usersIdResetPassword(id),
      null,
      () => i18n.t("user.password-reset-failed"),
      () => i18n.t("user.password-has-been-reset-to-the-default-password")
    );
  },
  async createAPIToken(name) {
    const response = await apiReq.post(API_ROUTES.usersApiTokens, { name });
    return response.data;
  },
  async deleteAPIToken(id) {
    const response = await apiReq.delete(API_ROUTES.usersApiTokensTokenId(id));
    return response.data;
  },
  /** Adds a Recipe to the users favorites
   * @param id
   */
  async getFavorites(id) {
    const response = await apiReq.get(API_ROUTES.usersIdFavorites(id));
    return response.data;
  },
  /** Adds a Recipe to the users favorites
   * @param id
   */
  async addFavorite(id, slug) {
    const response = await apiReq.post(API_ROUTES.usersIdFavoritesSlug(id, slug));
    return response.data;
  },
  /** Adds a Recipe to the users favorites
   * @param id
   */
  async removeFavorite(id, slug) {
    const response = await apiReq.delete(API_ROUTES.usersIdFavoritesSlug(id, slug));
    return response.data;
  },

  userProfileImage(id) {
    if (!id || id === undefined) return;
    return `/api/users/${id}/image`;
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
