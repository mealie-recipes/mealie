import { ValidatorsApi } from "./public/validators";
import { ExploreApi } from "./public/explore";
import { SharedApi } from "./public/shared";
import { ApiRequestInstance } from "~/lib/api/types/non-generated";

export class PublicApi {
  public validators: ValidatorsApi;
  public explore: ExploreApi;
  public shared: SharedApi;

  constructor(requests: ApiRequestInstance) {
    this.validators = new ValidatorsApi(requests);
    this.explore = new ExploreApi(requests);
    this.shared = new SharedApi(requests);

    Object.freeze(this);
  }
}
