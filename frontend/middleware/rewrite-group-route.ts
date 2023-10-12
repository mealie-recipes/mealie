import { Middleware } from "@nuxt/types"
import { useUserApi } from "~/composables/api";

// async function insertGroupSlugIntoRoute(routeVal: string) {
//   const api = useUserApi();
//   const { data: group } = await api.groups.getCurrentUserGroup();
//   if (!group) {
//     return;
//   }

//   routeVal = routeVal || "/";
//   if (routeVal[0] !== "/") {
//     routeVal = `/${routeVal}`;
//   }

//   const routeComponents = routeVal.split("/");
//   if (routeComponents.length < 2 || routeComponents[1].toLowerCase() !== group.slug.toLowerCase()) {
//     return `/${group.slug}${routeVal}`;
//   }

//   return routeVal;
// }

const rewriteGroupRoute: Middleware = (context) => {
  // if (!context.store.app.router) {
  //   return;
  // }

  // context.store.app.router.beforeEach(async (to, from) => {
  //   return await insertGroupSlugIntoRoute(to.fullPath);
  // })
}

export default rewriteGroupRoute
