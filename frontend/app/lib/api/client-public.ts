import { ValidatorsApi } from "./public/validators";
import { ExploreApi } from "./public/explore";
import { SharedApi } from "./public/shared";
import type { ApiRequestInstance } from "~/lib/api/types/non-generated";

export class PublicApi {
  public validators: ValidatorsApi;
  public shared: SharedApi;

  constructor(requests: ApiRequestInstance) {
    this.validators = new ValidatorsApi(requests);
    this.shared = new SharedApi(requests);
  }
}

export class PublicExploreApi extends PublicApi {
  public explore: ExploreApi;

  constructor(requests: ApiRequestInstance, groupSlug: string) {
    super(requests);
    this.explore = new ExploreApi(requests, groupSlug);

    Object.freeze(this);
  }
}
