import { apiReq } from "./api-utils";

export const utilsAPI = {
  // import { api } from "@/api";
  async uploadFile(url, fileObject) {
    console.log("API Called");

    let response = await apiReq.post(url, fileObject, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response;
  },
};
