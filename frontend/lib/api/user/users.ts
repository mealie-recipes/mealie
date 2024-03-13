import { BaseCRUDAPI } from "../base/base-clients";
import { QueryValue, route } from "~/lib/api/base/route";
import { PaginationData, RequestResponse } from "~/lib/api/types/non-generated";
import {
  ChangePassword,
  DeleteTokenResponse,
  GroupInDB,
  LongLiveTokenIn,
  LongLiveTokenOut,
  ResetPassword,
  UserBase,
  UserFavorites,
  UserIn,
  UserOut,
  UserSummary,
} from "~/lib/api/types/user";

const prefix = "/api";

const routes = {
  groupUsers: `${prefix}/users/group-users`,
  usersSelf: `${prefix}/users/self`,
  groupsSelf: `${prefix}/users/self/group`,
  passwordReset: `${prefix}/users/reset-password`,
  passwordChange: `${prefix}/users/password`,
  users: `${prefix}/users`,

  usersIdImage: (id: string) => `${prefix}/users/${id}/image`,
  usersIdResetPassword: (id: string) => `${prefix}/users/${id}/reset-password`,
  usersId: (id: string) => `${prefix}/users/${id}`,
  usersIdFavorites: (id: string) => `${prefix}/users/${id}/favorites`,
  usersIdFavoritesSlug: (id: string, slug: string) => `${prefix}/users/${id}/favorites/${slug}`,

  usersApiTokens: `${prefix}/users/api-tokens`,
  usersApiTokensTokenId: (token_id: string | number) => `${prefix}/users/api-tokens/${token_id}`,
};

export class UserApi extends BaseCRUDAPI<UserIn, UserOut, UserBase> {
  baseRoute: string = routes.users;
  itemRoute = (itemid: string) => routes.usersId(itemid);

  async getGroupUsers(page = 1, perPage = -1, params = {} as Record<string, QueryValue>) {
    return await this.requests.get<PaginationData<UserSummary>>(route(routes.groupUsers, { page, perPage, ...params }));
  }

  async getSelfGroup(): Promise<RequestResponse<GroupInDB>> {
    return await this.requests.get(routes.groupsSelf, {});
  }

  async addFavorite(id: string, slug: string) {
    return await this.requests.post(routes.usersIdFavoritesSlug(id, slug), {});
  }

  async removeFavorite(id: string, slug: string) {
    return await this.requests.delete(routes.usersIdFavoritesSlug(id, slug));
  }

  async getFavorites(id: string) {
    return await this.requests.get<UserFavorites>(routes.usersIdFavorites(id));
  }

  async changePassword(changePassword: ChangePassword) {
    return await this.requests.put(routes.passwordChange, changePassword);
  }

  async createAPIToken(tokenName: LongLiveTokenIn) {
    return await this.requests.post<LongLiveTokenOut>(routes.usersApiTokens, tokenName);
  }

  async deleteAPIToken(tokenId: number) {
    return await this.requests.delete<DeleteTokenResponse>(routes.usersApiTokensTokenId(tokenId));
  }

  userProfileImage(id: string) {
    if (!id || id === undefined) return;
    return `/api/users/${id}/image`;
  }

  async resetPassword(payload: ResetPassword) {
    return await this.requests.post(routes.passwordReset, payload);
  }
}
