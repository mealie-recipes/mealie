import { BaseCRUDAPI } from "./_base";
import { GroupInDB } from "~/types/api-types/user";

const prefix = "/api";

const routes = {
  groups: `${prefix}/groups`,
  groupsSelf: `${prefix}/groups/self`,
  categories: `${prefix}/groups/categories`,

  preferences: `${prefix}/groups/preferences`,

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

export interface UpdatePreferences {
  privateGroup: boolean;
  firstDayOfWeek: number;
  recipePublic: boolean;
  recipeShowNutrition: boolean;
  recipeShowAssets: boolean;
  recipeLandscapeView: boolean;
  recipeDisableComments: boolean;
  recipeDisableAmount: boolean;
}

export interface Preferences extends UpdatePreferences {
  id: number;
  group_id: number;
}

export interface Group extends CreateGroup {
  id: number;
  preferences: Preferences;
}

export class GroupAPI extends BaseCRUDAPI<GroupInDB, CreateGroup> {
  baseRoute = routes.groups;
  itemRoute = routes.groupsId;
  /** Returns the Group Data for the Current User
   */
  async getCurrentUserGroup() {
    return await this.requests.get<Group>(routes.groupsSelf);
  }

  async getCategories() {
    return await this.requests.get<Category[]>(routes.categories);
  }

  async setCategories(payload: Category[]) {
    return await this.requests.put<Category[]>(routes.categories, payload);
  }

  async getPreferences() {
    return await this.requests.get<Preferences>(routes.preferences);
  }

  async setPreferences(payload: UpdatePreferences) {
    return await this.requests.put<Preferences>(routes.preferences, payload);
  }
}
