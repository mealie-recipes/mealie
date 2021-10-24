import { BaseAPI } from "../_base";

export interface RegisterPayload {
  group: string;
  groupToken: string;
  email: string;
  password: string;
  passwordConfirm: string;
  advanced: boolean;
  private: boolean;
}

const prefix = "/api";

const routes = {
  register: `${prefix}/users/register`,
};

export class RegisterAPI extends BaseAPI {
  /** Returns a list of avaiable .zip files for import into Mealie.
   */
  async register(payload: RegisterPayload) {
    return await this.requests.post<any>(routes.register, payload);
  }
}
