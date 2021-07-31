import { apiReq } from "./api-utils";
import i18n from "@/i18n.js";
import { API_ROUTES } from "./apiRoutes";

function deleteErrorText(response) {
  switch (response.data.detail) {
    case "GROUP_WITH_USERS":
      return i18n.t("group.cannot-delete-group-with-users");

    case "GROUP_NOT_FOUND":
      return i18n.t("group.group-not-found");

    case "DEFAULT_GROUP":
      return i18n.t("group.cannot-delete-default-group");

    default:
      return i18n.t("group.group-deletion-failed");
  }
}

export const groupAPI = {
  async allGroups() {
    let response = await apiReq.get(API_ROUTES.groups);
    return response.data;
  },
  create(name) {
    return apiReq.post(
      API_ROUTES.groups,
      { name: name },
      () => i18n.t("group.user-group-creation-failed"),
      () => i18n.t("group.user-group-created")
    );
  },
  delete(id) {
    return apiReq.delete(API_ROUTES.groupsId(id), null, deleteErrorText, function() {
      return i18n.t("group.group-deleted");
    });
  },
  async current() {
    const response = await apiReq.get(API_ROUTES.groupsSelf, null, null);
    if (response) {
      return response.data;
    }
  },
  update(data) {
    return apiReq.put(
      API_ROUTES.groupsId(data.id),
      data,
      () => i18n.t("group.error-updating-group"),
      () => i18n.t("settings.group-settings-updated")
    );
  },
};
