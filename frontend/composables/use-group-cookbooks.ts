import { useAsyncKey } from "./use-utils";
import { usePublicExploreApi } from "./api/api-client";
import { useUserApi } from "~/composables/api";

export const useCookbook = function (publicGroupSlug: string | null = null) {
  function getOne(id: string | number) {
    // passing the group slug switches to using the public API
    const api = publicGroupSlug ? usePublicExploreApi(publicGroupSlug).explore : useUserApi();

    const { data: units } = useAsyncData(useAsyncKey(), async () => {
      const { data } = await api.cookbooks.getOne(id);

      return data;
    });

    return units;
  }

  return { getOne };
};
