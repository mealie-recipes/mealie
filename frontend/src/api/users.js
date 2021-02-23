import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
const authPrefix = baseURL + "auth";
const userPrefix = baseURL + "users";

const authURLs = {
  token: `${authPrefix}/token`,
};

const usersURLs = {
  users: `${userPrefix}`,
  self: `${userPrefix}/self`,
  userID: id => `${userPrefix}/${id}`,
};

export default {
  async login(formData) {
    let response = await apiReq.post(authURLs.token, formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
    return response;
  },
  async allUsers() {
    let response = await apiReq.get(usersURLs.users);
    return response.data;
  },
  async create(user) {
    let response = await apiReq.post(usersURLs.users, user);
    return response.data;
  },
  async self() {
    let response = await apiReq.get(usersURLs.self);
    return response.data;
  },
  async byID(id) {
    let response = await apiReq.get(usersURLs.userID(id));
    return response.data;
  },
  async update(user) {
    let response = await apiReq.put(usersURLs.userID(user.id), user);
    return response.data;
  },
  async delete(id) {
    let response = await apiReq.delete(usersURLs.userID(id));
    return response.data;
  },
};
