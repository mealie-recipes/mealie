import { apiReq } from "./api-utils";

export default {
  // import { api } from "@/api";
  async uploadFile(url, fileObject) {
    let response = await apiReq.post(url, fileObject, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },
};
