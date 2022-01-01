import { BaseAPI } from "../_base";

const prefix = "/api";

export class UtilsAPI extends BaseAPI {
  async download(url: string) {
    const { response } = await this.requests.get(url);

    if (!response) {
      return;
    }

    // @ts-ignore
    const token: string = response.data.fileToken;

    const tokenURL = prefix + "/utils/download?token=" + token;
    window.open(tokenURL, "_blank");
    return await response;
  }
}
