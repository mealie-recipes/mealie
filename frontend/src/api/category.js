import { baseURL } from "./api-utils";
import { apiReq } from "./api-utils";

const categoryBase = baseURL + "category/";

const categoryURLs = {
    get_all: `${categoryBase}all`,
  };
 
export default {
    async get_all() {
      let response = await apiReq.get(categoryURLs.get_all);
      return response;
    },
}