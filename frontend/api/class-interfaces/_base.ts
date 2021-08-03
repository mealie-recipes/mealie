import { ApiRequestInstance } from "~/types/api";

export interface CrudAPIInterface {
  requests: ApiRequestInstance;

  // Route Properties / Methods
  baseRoute: string;
  itemRoute(itemId: string): string;

  // Methods
}

export abstract class BaseAPIClass<T> implements CrudAPIInterface {
  requests: ApiRequestInstance;

  abstract baseRoute: string;
  abstract itemRoute(itemId: string): string;

  constructor(requests: ApiRequestInstance) {
    this.requests = requests;
  }

  async getAll(start = 0, limit = 9999) {
    return await this.requests.get<T[]>(this.baseRoute, {
      params: { start, limit },
    });
  }

  async getOne(itemId: string) {
    return await this.requests.get<T>(this.itemRoute(itemId));
  }

  async createOne(payload: T) {
    return await this.requests.post(this.baseRoute, payload);
  }
  
  async updateOne(itemId: string, payload: T){
    return await this.requests.put<T>(this.itemRoute(itemId), payload);
  }

  async patchOne(itemId: string, payload: T) {
    return await this.requests.patch(this.itemRoute(itemId), payload);
  }

  async deleteOne(itemId: string) {
    return await this.requests.delete<T>(this.itemRoute(itemId));
  }

}
