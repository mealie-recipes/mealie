import { ApiRequestInstance } from "~/types/api";

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

export abstract class BaseCRUDAPI<T, U> extends BaseAPI implements CrudAPIInterface {
  abstract baseRoute: string;
  abstract itemRoute(itemId: string | number): string;

  async getAll(start = 0, limit = 9999, params = {} as any) {
    return await this.requests.get<T[]>(this.baseRoute, {
      params: { start, limit, ...params },
    });
  }

  async createOne(payload: U) {
    return await this.requests.post<T>(this.baseRoute, payload);
  }

  async getOne(itemId: string | number) {
    return await this.requests.get<T>(this.itemRoute(itemId));
  }

  async updateOne(itemId: string | number, payload: T) {
    return await this.requests.put<T>(this.itemRoute(itemId), payload);
  }

  async patchOne(itemId: string, payload: T) {
    return await this.requests.patch(this.itemRoute(itemId), payload);
  }

  async deleteOne(itemId: string | number) {
    return await this.requests.delete<T>(this.itemRoute(itemId));
  }
}
