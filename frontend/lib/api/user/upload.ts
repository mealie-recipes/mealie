import { BaseAPI } from "../base/base-clients";

export class UploadFile extends BaseAPI {
  file(url: string, fileObject: any) {
    const { $axios } = useNuxtApp();
    return $axios.post<string>(url, fileObject, { headers: { "Content-Type": "multipart/form-data" } });
    // return this.requests.post<string>(url, fileObject);
  }
}
