import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
const groupPrefix = baseURL + "groups";

const groupsURLs = {
  groups: `${groupPrefix}`,
  create: `${groupPrefix}`,
  delete: id => `${groupPrefix}/${id}`,
  current: `${groupPrefix}/self`,
  update: id => `${groupPrefix}/${id}`,
};

export const groupAPI = {
  async allGroups() {
    let response = await apiReq.get(groupsURLs.groups);
    return response.data;
  },
  async create(name) {
    let response = await apiReq.post(groupsURLs.create, { name: name });
    return response;
  },
  async delete(id) {
    let response = await apiReq.delete(groupsURLs.delete(id));
    return response;
  },
  async current() {
    let response = await apiReq.get(groupsURLs.current);
    return response.data;
  },
  async update(data) {
    let response = await apiReq.put(groupsURLs.update(data.id), data);
    return response;
  },
};
