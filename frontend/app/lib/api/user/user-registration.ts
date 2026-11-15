import { BaseAPI } from "../base/base-clients";
import type { UserRegistrationCreate } from "~/lib/api/types/user";

const prefix = "/api";

const routes = {
  register: `${prefix}/users/register`,
};

export class RegisterAPI extends BaseAPI {
  async register(payload: UserRegistrationCreate) {
    return await this.requests.post<any>(routes.register, payload);
  }
}
