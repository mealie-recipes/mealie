import { BaseAPI } from "../_base";

const prefix = "/api";

interface DownloadData {
  fileToken: string,
}

export class UtilsAPI extends BaseAPI {
  async download(url: string) {
    const { response } = await this.requests.get<DownloadData>(url);

    if (!response) {
      return;
    }

    const token: string = response.data.fileToken;

    const tokenURL = prefix + "/utils/download?token=" + token;
    window.open(tokenURL, "_blank");
    return response;
  }
}
