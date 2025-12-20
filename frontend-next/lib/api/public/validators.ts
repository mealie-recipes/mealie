import { ValidationResponse } from "../../types/validations";
import { apiRequest } from "../base/api-request-adapter";
import { BaseAPI } from "../base/base-api";
import { API_ROUTES } from "../routes";

export class ValidatorsApi extends BaseAPI {
  constructor() {
    super(apiRequest);
  }

  async validateAvailability(
    type: "group" | "user" | "email" | "recipe",
    value: string,
    groupId?: string
  ) {
    switch (type) {
      case "group": {
        const response = await this.requests.get<ValidationResponse>(
          API_ROUTES.PUBLIC_ROUTES.VALIDATORS.group(value)
        );
        return response.valid;
      }
      case "user": {
        const response = await this.requests.get<ValidationResponse>(
          API_ROUTES.PUBLIC_ROUTES.VALIDATORS.user(value)
        );
        return response.valid;
      }
      case "email": {
        const response = await this.requests.get<ValidationResponse>(
          API_ROUTES.PUBLIC_ROUTES.VALIDATORS.email(value)
        );
        return response.valid;
      }
      case "recipe": {
        if (!groupId) {
          throw new Error("groupId is required for recipe validation");
        }
        const response = await this.requests.get<ValidationResponse>(
          API_ROUTES.PUBLIC_ROUTES.VALIDATORS.recipe(groupId, value)
        );
        return response.valid;
      }
      default:
        throw new Error(`Unknown validation type: ${type}`);
    }
  }
}

export const validatorsApi = new ValidatorsApi();
