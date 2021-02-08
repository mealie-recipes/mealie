import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const prefix = baseURL + "debug";

const debugURLs = {
  version: `${prefix}/version`,
};

export default {
  async get_version() {
    let response = await apiReq.get(debugURLs.version);
    return response.data;
  },
};
