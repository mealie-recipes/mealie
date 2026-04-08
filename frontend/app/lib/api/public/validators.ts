import { BaseAPI } from "../base/base-clients";
import { ValidationResponse } from "~/lib/api/types/response";

const prefix = "/api";

const routes = {
  group: (name: string) => `${prefix}/validators/group?name=${name}`,
  user: (name: string) => `${prefix}/validators/user/name?name=${name}`,
  email: (name: string) => `${prefix}/validators/user/email?email=${name}`,
  recipe: (groupId: string, name: string) => `${prefix}/validators/group/recipe?group_id=${groupId}?name=${name}`,
};

export class ValidatorsApi extends BaseAPI {
  async group(name: string) {
    return await this.requests.get<ValidationResponse>(routes.group(name));
  }

  async username(name: string) {
    return await this.requests.get<ValidationResponse>(routes.user(name));
  }

  async email(email: string) {
    return await this.requests.get<ValidationResponse>(routes.email(email));
  }

  async recipe(groupId: string, name: string) {
    return await this.requests.get<ValidationResponse>(routes.recipe(groupId, name));
  }
}
