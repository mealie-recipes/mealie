import type { Recipe } from "../types/recipe";
import type { ApiRequestInstance, PaginationData } from "~/lib/api/types/non-generated";
import { type QueryValue, route } from "~/lib/api/base/route";

export interface CrudAPIInterface {
  requests: ApiRequestInstance;

  // Route Properties / Methods
  baseRoute: string;
  itemRoute(itemId: string | number): string;

  // Methods
}

export abstract class BaseAPI {
  requests: ApiRequestInstance;

  constructor(requests: ApiRequestInstance) {
    this.requests = requests;
  }
}

export abstract class BaseCRUDAPIReadOnly<ReadType>
  extends BaseAPI
  implements CrudAPIInterface {
  public baseRoute: string;
  public itemRouteFn: (itemId: string | number) => string;

  constructor(
    requests: ApiRequestInstance,
    baseRoute: string,
    itemRoute: (itemId: string | number) => string,
  ) {
    super(requests);
    this.baseRoute = baseRoute;
    this.itemRouteFn = itemRoute;
  }

  get baseRouteValue() {
    return this.baseRoute;
  }

  itemRoute(itemId: string | number): string {
    return this.itemRouteFn(itemId);
  }

  async getAll(page = 1, perPage = -1, params = {} as Record<string, QueryValue>) {
    params = Object.fromEntries(Object.entries(params).filter(([_, v]) => v !== null && v !== undefined));
    return await this.requests.get<PaginationData<ReadType>>(route(this.baseRoute, { page, perPage, ...params }));
  }

  async getOne(itemId: string | number) {
    return await this.requests.get<ReadType>(this.itemRoute(itemId));
  }
}

export abstract class BaseCRUDAPI<CreateType, ReadType, UpdateType = CreateType>
  extends BaseCRUDAPIReadOnly<ReadType>
  implements CrudAPIInterface {
  async createOne(payload: CreateType) {
    return await this.requests.post<ReadType>(this.baseRoute, payload);
  }

  async updateOne(itemId: string | number, payload: UpdateType) {
    return await this.requests.put<ReadType, UpdateType>(this.itemRoute(itemId), payload);
  }

  async patchOne(itemId: string, payload: Partial<UpdateType>) {
    return await this.requests.patch<ReadType, Partial<UpdateType>>(this.itemRoute(itemId), payload);
  }

  async deleteOne(itemId: string | number) {
    return await this.requests.delete<ReadType>(this.itemRoute(itemId));
  }

  async duplicateOne(itemId: string | number, newName: string | undefined) {
    return await this.requests.post<Recipe>(`${this.itemRoute(itemId)}/duplicate`, {
      name: newName,
    });
  }
}
