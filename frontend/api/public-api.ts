import { ValidatorsApi } from "./public/validators";
import { ApiRequestInstance } from "~/types/api";

export class PublicApi {
  public validators: ValidatorsApi;

  constructor(requests: ApiRequestInstance) {
    this.validators = new ValidatorsApi(requests);

    Object.freeze(this);
  }
}
