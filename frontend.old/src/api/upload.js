import { apiReq } from "./api-utils";
import i18n from "@/i18n.js";

export const utilsAPI = {
  // import { api } from "@/api";
  uploadFile(url, fileObject) {
    return apiReq.post(
      url,
      fileObject,
      () => i18n.t("general.failure-uploading-file"),
      () => i18n.t("general.file-uploaded")
    );
  },
};
