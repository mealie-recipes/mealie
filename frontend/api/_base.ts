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

export abstract class BaseCRUDAPI<CreateType, ReadType, UpdateType=CreateType> extends BaseAPI implements CrudAPIInterface {
  abstract baseRoute: string;
  abstract itemRoute(itemId: string | number): string;

  async getAll(start = 0, limit = 9999, params = {} as any) {
    return await this.requests.get<ReadType[]>(this.baseRoute, {
      params: { start, limit, ...params },
    });
  }

  async createOne(payload: CreateType) {
    return await this.requests.post<ReadType>(this.baseRoute, payload);
  }

  async getOne(itemId: string | number) {
    return await this.requests.get<ReadType>(this.itemRoute(itemId));
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
}
