import { useAsync, useContext, useRoute } from "@nuxtjs/composition-api";
import { useUserApi } from "./api";

export const useGroupSlugRoute = function () {
  const { $auth } = useContext();
  const route = useRoute();
  const api = useUserApi();

  async function getGroupSlug() {
    if (!$auth.loggedIn) {
      return route.value.params.groupSlug;
    }

    const { data: group } = await api.groups.getCurrentUserGroup();
    return group ? group.slug.toLowerCase() : null;
  }

  const asyncKey = $auth.user?.id ? String($auth.user.groupId) : String(Date.now());
  const groupSlug = useAsync(async () => await getGroupSlug(), asyncKey);
  return { groupSlug, getGroupSlug }
};
