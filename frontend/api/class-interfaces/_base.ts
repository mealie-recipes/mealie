import { ApiRequestInstance } from "~/types/api";

export interface CrudAPIInterface {
  requests: ApiRequestInstance;

  // Route Properties / Methods
  baseRoute: string;
  itemRoute(itemId: string): string;

  // Methods
}

export const crudMixins = <T>(
  requests: ApiRequestInstance,
  baseRoute: string,
  itemRoute: (itemId: string) => string
) => {
  async function getAll(start = 0, limit = 9999) {
    return await requests.get<T[]>(baseRoute, {
      params: { start, limit },
    });
  }

  async function getOne(itemId: string) {
    return await requests.get<T>(itemRoute(itemId));
  }

  async function updateOne(itemId: string, payload: T) {
    return await requests.put<T>(itemRoute(itemId), payload);
  }

  async function patchOne(itemId: string, payload: T) {
    return await requests.patch(itemRoute(itemId), payload);
  }

  async function deleteOne(itemId: string) {
    return await requests.delete<T>(itemRoute(itemId));
  }

  return { getAll, getOne, updateOne, patchOne, deleteOne };
};

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

  async updateOne(itemId: string, payload: T) {
    return await this.requests.put<T>(this.itemRoute(itemId), payload);
  }

  async patchOne(itemId: string, payload: T) {
    return await this.requests.patch(this.itemRoute(itemId), payload);
  }

  async deleteOne(itemId: string) {
    return await this.requests.delete<T>(this.itemRoute(itemId));
  }
}
