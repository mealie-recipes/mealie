import { BaseCRUDAPI } from "./_base";
import { UserIn, UserOut } from "~/types/api-types/user";

// Interfaces

interface ChangePassword {
  currentPassword: string;
  newPassword: string;
}

interface CreateAPIToken {
  name: string;
}

// Code

const prefix = "/api";

const routes = {
  usersSelf: `${prefix}/users/self`,
  users: `${prefix}/users`,

  usersIdImage: (id: string) => `${prefix}/users/${id}/image`,
  usersIdResetPassword: (id: string) => `${prefix}/users/${id}/reset-password`,
  usersId: (id: string) => `${prefix}/users/${id}`,
  usersIdPassword: (id: string) => `${prefix}/users/${id}/password`,
  usersIdFavorites: (id: string) => `${prefix}/users/${id}/favorites`,
  usersIdFavoritesSlug: (id: string, slug: string) => `${prefix}/users/${id}/favorites/${slug}`,

  usersApiTokens: `${prefix}/users/api-tokens`,
  usersApiTokensTokenId: (token_id: string) => `${prefix}/users/api-tokens/${token_id}`,
};

export class UserApi extends BaseCRUDAPI<UserOut, UserIn> {
  baseRoute: string = routes.users;
  itemRoute = (itemid: string) => routes.usersId(itemid);

  async addFavorite(id: string, slug: string) {
    return await this.requests.post(routes.usersIdFavoritesSlug(id, slug), {});
  }

  async removeFavorite(id: string, slug: string) {
    return await this.requests.delete(routes.usersIdFavoritesSlug(id, slug));
  }

  async getFavorites(id: string) {
    await this.requests.get(routes.usersIdFavorites(id));
  }

  async changePassword(id: string, changePassword: ChangePassword) {
    return await this.requests.put(routes.usersIdPassword(id), changePassword);
  }

  async resetPassword(id: string) {
    return await this.requests.post(routes.usersIdResetPassword(id), {});
  }

  async createAPIToken(tokenName: CreateAPIToken) {
    return await this.requests.post(routes.usersApiTokens, tokenName);
  }

  async deleteApiToken(tokenId: string) {
    return await this.requests.delete(routes.usersApiTokensTokenId(tokenId));
  }

  userProfileImage(id: string) {
    if (!id || id === undefined) return;
    return `/api/users/${id}/image`;
  }
}
