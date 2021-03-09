import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
const groupPrefix = baseURL + "groups";

const groupsURLs = {
  groups: `${groupPrefix}`,
};

export default {
  async allGroups() {
    let response = await apiReq.get(groupsURLs.groups);
    return response.data;
  },
};
