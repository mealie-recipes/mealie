import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";
import axios from "axios";
const authPrefix = baseURL + "auth";
const userPrefix = baseURL + "users";

const authURLs = {
  token: `${authPrefix}/token`,
  refresh: `${authPrefix}/refresh`,
};

const usersURLs = {
  users: `${userPrefix}`,
  self: `${userPrefix}/self`,
  userID: id => `${userPrefix}/${id}`,
  password: id => `${userPrefix}/${id}/password`,
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
  async refresh() {
    let response = await axios.get(authURLs.refresh).catch(function(event) {
      console.log("Fetch failed", event);
    });
    return response.data ? response.data : false;
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
  async changePassword(id, password) {
    let response = await apiReq.put(usersURLs.password(id), password);
    return response.data;
  },
  async delete(id) {
    let response = await apiReq.delete(usersURLs.userID(id));
    return response.data;
  },
};
