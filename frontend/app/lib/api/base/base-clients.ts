import type { AxiosRequestConfig } from "axios";
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

  async getAll(page = 1, perPage = -1, params = {} as Record<string, QueryValue>, config?: AxiosRequestConfig) {
    params = Object.fromEntries(Object.entries(params).filter(([_, v]) => v !== null && v !== undefined));
    return await this.requests.get<PaginationData<ReadType>>(route(this.baseRoute, { page, perPage, ...params }), undefined, config);
  }

  async getOne(itemId: string | number, config?: AxiosRequestConfig) {
    return await this.requests.get<ReadType>(this.itemRoute(itemId), undefined, config);
  }
}

export abstract class BaseCRUDAPI<CreateType, ReadType, UpdateType = CreateType>
  extends BaseCRUDAPIReadOnly<ReadType>
  implements CrudAPIInterface {
  async createOne(payload: CreateType, config?: AxiosRequestConfig) {
    return await this.requests.post<ReadType>(this.baseRoute, payload, config);
  }

  async updateOne(itemId: string | number, payload: UpdateType, config?: AxiosRequestConfig) {
    return await this.requests.put<ReadType, UpdateType>(this.itemRoute(itemId), payload, config);
  }

  async patchOne(itemId: string, payload: Partial<UpdateType>, config?: AxiosRequestConfig) {
    return await this.requests.patch<ReadType, Partial<UpdateType>>(this.itemRoute(itemId), payload, config);
  }

  async deleteOne(itemId: string | number, config?: AxiosRequestConfig) {
    return await this.requests.delete<ReadType>(this.itemRoute(itemId), config);
  }

  async duplicateOne(itemId: string | number, newName: string | undefined, config?: AxiosRequestConfig) {
    return await this.requests.post<Recipe>(`${this.itemRoute(itemId)}/duplicate`, {
      name: newName,
    }, config);
  }
}
