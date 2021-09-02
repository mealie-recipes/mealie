import { BaseCRUDAPI } from "./_base";
import { GroupInDB } from "~/types/api-types/user";

const prefix = "/api";

const routes = {
  groups: `${prefix}/groups`,
  groupsSelf: `${prefix}/groups/self`,
  categories: `${prefix}/groups/categories`,

  groupsId: (id: string | number) => `${prefix}/groups/${id}`,
};

interface Category {
  id: number;
  name: string;
  slug: string;
}

export interface CreateGroup {
  name: string;
}

export class GroupAPI extends BaseCRUDAPI<GroupInDB, CreateGroup> {
  baseRoute = routes.groups;
  itemRoute = routes.groupsId;
  /** Returns the Group Data for the Current User
   */
  async getCurrentUserGroup() {
    return await this.requests.get(routes.groupsSelf);
  }

  async getCategories() {
    return await this.requests.get<Category[]>(routes.categories);
  }

  async setCategories(payload: Category[]) {
    return await this.requests.put<Category[]>(routes.categories, payload);
  }
}
