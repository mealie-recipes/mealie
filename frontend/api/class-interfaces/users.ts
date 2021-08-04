import { BaseAPIClass } from "./_base";
import { UserOut } from "~/types/api-types/user";

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
};

export class UserApi extends BaseAPIClass<UserOut> {
    baseRoute: string = routes.users;
    itemRoute = (itemid: string) => routes.usersId(itemid);

    async addFavorite(id: string, slug: string) {
        const response = await this.requests.post(routes.usersIdFavoritesSlug(id, slug), {});
        return response.data;
      }

      async removeFavorite(id: string, slug: string) {
        const response = await this.requests.delete(routes.usersIdFavoritesSlug(id, slug));
        return response.data;
      }
}
