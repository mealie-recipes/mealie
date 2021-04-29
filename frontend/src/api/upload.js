import { apiReq } from "./api-utils";
import i18n from '@/i18n.js';

export const utilsAPI = {
  // import { api } from "@/api";
  uploadFile(url, fileObject) {
    console.log("API Called");

    return apiReq.post(
      url,
      fileObject,
      function() { return i18n.t('general.failure-uploading-file'); },
      function() { return i18n.t('general.file-uploaded'); }
    );
  },
};
