import { BaseAPI } from "../_base";
import { CreateUserRegistration } from "~/types/api-types/user";

const prefix = "/api";

const routes = {
  register: `${prefix}/users/register`,
};

export class RegisterAPI extends BaseAPI {
  /** Returns a list of avaiable .zip files for import into Mealie.
   */
  async register(payload: CreateUserRegistration) {
    return await this.requests.post<any>(routes.register, payload);
  }
}
