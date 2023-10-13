import { useAsync, useContext, useRoute } from "@nuxtjs/composition-api";
import { useUserApi } from "./api";

export const useGroupSlugRoute = function () {
  const { $auth } = useContext();
  const route = useRoute();
  const api = useUserApi();

  async function getGroupSlug() {
    if (route.value.params.groupSlug) {
      return route.value.params.groupSlug;
    } else if (!$auth.loggedIn) {
      return null;
    }

    const { data: group } = await api.groups.getCurrentUserGroup();
    return group ? group.slug.toLowerCase() : null;
  }

  const asyncKey = String(Date.now());
  const groupSlug = useAsync(async () => await getGroupSlug(), asyncKey);
  return { groupSlug, getGroupSlug }
};
