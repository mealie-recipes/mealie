import { ValidatorsApi } from "./public/validators";
import { ExploreApi } from "./public/explore";
import { ApiRequestInstance } from "~/types/api";

export class PublicApi {
  public validators: ValidatorsApi;
  public explore: ExploreApi;

  constructor(requests: ApiRequestInstance) {
    this.validators = new ValidatorsApi(requests);
    this.explore = new ExploreApi(requests);

    Object.freeze(this);
  }
}
