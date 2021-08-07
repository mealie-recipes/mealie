import { BaseAPI } from "./_base";

export class UploadFile extends BaseAPI {
  file(url: string, fileObject: any) {
    return this.requests.post(url, fileObject);
  }
}
