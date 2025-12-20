import { ApiRequestInstance } from "../types";
import { QueryValue, route } from "./route";

export interface CrudAPIInterface {
  baseRoute: string;
}

export abstract class BaseAPI {
  protected requests: ApiRequestInstance;

  constructor(requests: ApiRequestInstance) {
    this.requests = requests;
  }
}

export abstract class BaseCRUDAPIReadOnly<ReadType>
  extends BaseAPI
  implements CrudAPIInterface
{
  public baseRoute: string;

  constructor(requests: ApiRequestInstance, baseRoute: string) {
    super(requests);
    this.baseRoute = baseRoute;
  }

  /**
   * Helper to construct item routes like /recipes/123
   */
  protected itemRoute(itemId: string | number): string {
    return `${this.baseRoute}/${itemId}`;
  }

  async getAll(
    page = 1,
    perPage = -1,
    params = {} as Record<string, QueryValue>
  ) {
    // Clean params
    const cleanParams = Object.fromEntries(
      Object.entries(params).filter(([_, v]) => v !== null && v !== undefined)
    );

    // Use your route helper, or just append query string
    const url = route(this.baseRoute, { page, perPage, ...cleanParams });
    return await this.requests.get<ReadType[]>(url); // Assuming getAll returns an array
  }

  async getOne(itemId: string | number) {
    return await this.requests.get<ReadType>(this.itemRoute(itemId));
  }
}

export abstract class BaseCRUDAPI<
  CreateType,
  ReadType,
  UpdateType = CreateType
> extends BaseCRUDAPIReadOnly<ReadType> {
  async createOne(payload: CreateType) {
    return await this.requests.post<ReadType>(this.baseRoute, payload);
  }

  async updateOne(itemId: string | number, payload: UpdateType) {
    return await this.requests.put<ReadType>(this.itemRoute(itemId), payload);
  }

  async patchOne(itemId: string | number, payload: Partial<UpdateType>) {
    return await this.requests.patch<ReadType>(this.itemRoute(itemId), payload);
  }

  async deleteOne(itemId: string | number) {
    return await this.requests.delete<ReadType>(this.itemRoute(itemId));
  }
}
