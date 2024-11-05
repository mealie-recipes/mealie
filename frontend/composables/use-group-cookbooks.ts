import { useAsync, ref, Ref, useContext } from "@nuxtjs/composition-api";
import { useAsyncKey } from "./use-utils";
import { usePublicExploreApi } from "./api/api-client";
import { useHouseholdSelf } from "./use-households";
import { useUserApi } from "~/composables/api";
import { ReadCookBook, UpdateCookBook } from "~/lib/api/types/cookbook";

let cookbookStore: Ref<ReadCookBook[] | null> | null = null;

export const useCookbook = function (publicGroupSlug: string | null = null) {
  function getOne(id: string | number) {
    // passing the group slug switches to using the public API
    const api = publicGroupSlug ? usePublicExploreApi(publicGroupSlug).explore : useUserApi();

    const units = useAsync(async () => {
      const { data } = await api.cookbooks.getOne(id);

      return data;
    }, useAsyncKey());

    return units;
  }

  return { getOne };
};

export const usePublicCookbooks = function (groupSlug: string) {
  const api = usePublicExploreApi(groupSlug).explore;
  const loading = ref(false);

  const actions = {
    getAll() {
      loading.value = true;
      const units = useAsync(async () => {
        const { data } = await api.cookbooks.getAll(1, -1, { orderBy: "position", orderDirection: "asc" });

        if (data) {
          return data.items;
        } else {
          return null;
        }
      }, useAsyncKey());

      loading.value = false;
      return units;
    },
    async refreshAll() {
      loading.value = true;
      const { data } = await api.cookbooks.getAll(1, -1, { orderBy: "position", orderDirection: "asc" });

      if (data && data.items && cookbookStore) {
        cookbookStore.value = data.items;
      }

      loading.value = false;
    },
    flushStore() {
      cookbookStore = null;
    },
  };

  if (!cookbookStore) {
    cookbookStore = actions.getAll();
  }

  return { cookbooks: cookbookStore, actions };
}

export const useCookbooks = function () {
  const api = useUserApi();
  const { household } = useHouseholdSelf();
  const loading = ref(false);

  const { i18n } = useContext();

  const actions = {
    getAll() {
      loading.value = true;
      const units = useAsync(async () => {
        const { data } = await api.cookbooks.getAll(1, -1, { orderBy: "position", orderDirection: "asc" });

        if (data) {
          return data.items;
        } else {
          return null;
        }
      }, useAsyncKey());

      loading.value = false;
      return units;
    },
    async refreshAll() {
      loading.value = true;
      const { data } = await api.cookbooks.getAll(1, -1, { orderBy: "position", orderDirection: "asc" });

      if (data && data.items && cookbookStore) {
        cookbookStore.value = data.items;
      }

      loading.value = false;
    },
    async createOne(name: string | null = null) {
      loading.value = true;
      const { data } = await api.cookbooks.createOne({
        name: name || i18n.t("cookbook.household-cookbook-name", [household.value?.name || "", String((cookbookStore?.value?.length ?? 0) + 1)]) as string,
        position: (cookbookStore?.value?.length ?? 0) + 1,
        queryFilterString: "",
      });
      if (data && cookbookStore?.value) {
        cookbookStore.value.push(data);
      } else {
        this.refreshAll();
      }

      loading.value = false;
      return data;
    },
    async updateOne(updateData: UpdateCookBook) {
      if (!updateData.id) {
        return;
      }

      loading.value = true;
      const { data } = await api.cookbooks.updateOne(updateData.id, updateData);
      if (data && cookbookStore?.value) {
        this.refreshAll();
      }
      loading.value = false;
      return data;
    },

    async updateOrder(cookbooks: ReadCookBook[]) {
      if (!cookbooks?.length) {
        return;
      }

      loading.value = true;

      cookbooks.forEach((element, index) => {
        element.position = index + 1;
      });

      const { data } = await api.cookbooks.updateAll(cookbooks);

      if (data && cookbookStore?.value) {
        this.refreshAll();
      }

      loading.value = true;
    },
    async deleteOne(id: string | number) {
      loading.value = true;
      const { data } = await api.cookbooks.deleteOne(id);
      if (data && cookbookStore?.value) {
        this.refreshAll();
      }
    },
    flushStore() {
      cookbookStore = null;
    },
  };

  if (!cookbookStore) {
    cookbookStore = actions.getAll();
  }

  return { cookbooks: cookbookStore, actions };
};
