// This Content is Auto Generated
import { API_ROUTES } from "./apiRoutes";
import { apiReq } from "./api-utils";

export const shoppingListsAPI = {
  /** Create Shopping List in the Database
   */
  async createShoppingList(data) {
    const response = await apiReq.post(API_ROUTES.shoppingLists, data);
    return response.data;
  },
  /** Get Shopping List from the Database
   * @param id
   */
  async getShoppingList(id) {
    const response = await apiReq.get(API_ROUTES.shoppingListsId(id));
    return response.data;
  },
  /** Update Shopping List in the Database
   * @param id
   */
  async updateShoppingList(id, data) {
    const response = await apiReq.put(API_ROUTES.shoppingListsId(id), data);
    return response.data;
  },
  /** Delete Shopping List from the Database
   * @param id
   */
  async deleteShoppingList(id) {
    const response = await apiReq.delete(API_ROUTES.shoppingListsId(id));
    return response.data;
  },
};
