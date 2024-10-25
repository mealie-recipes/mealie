import { useAsync, ref, Ref, useContext } from "@nuxtjs/composition-api";
import { useAsyncKey } from "./use-utils";
import { usePublicExploreApi } from "./api/api-client";
import { useHouseholdSelf } from "./use-households";
import { useUserApi } from "~/composables/api";
import { ReadCookBook, UpdateCookBook } from "~/lib/api/types/cookbook";

interface StoreInterface {
  get ref(): Ref<ReadCookBook[] | null> | null;
  set ref(newValue: Ref<ReadCookBook[] | null> | null);
}

let _cookbookStore: Ref<ReadCookBook[] | null> | null = null;
let _myCookbookStore: Ref<ReadCookBook[] | null> | null = null;
let _publicCookbookStore: Ref<ReadCookBook[] | null> | null = null;

const cookbookStore: StoreInterface = {
  get ref() {
    return _cookbookStore;
  },
  set ref(newValue: Ref<ReadCookBook[] | null> | null) {
    _cookbookStore = newValue;
  },
};

const myCookbookStore: StoreInterface = {
  get ref() {
    return _myCookbookStore;
  },
  set ref(newValue: Ref<ReadCookBook[] | null> | null) {
    _myCookbookStore = newValue;
  },
};

const publicCookbookStore: StoreInterface = {
  get ref() {
    return _publicCookbookStore;
  },
  set ref(newValue: Ref<ReadCookBook[] | null> | null) {
    _publicCookbookStore = newValue;
  },
};

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

      if (data && data.items && publicCookbookStore.ref) {
        publicCookbookStore.ref.value = data.items;
      }

      loading.value = false;
    },
    flushStore() {
      publicCookbookStore.ref = null;
    },
  };

  if (!publicCookbookStore.ref) {
    publicCookbookStore.ref = actions.getAll();
  }

  return { cookbooks: publicCookbookStore.ref, actions };
}

function useCookbooksFactory(store: StoreInterface, onlyMine = false) {
  const api = useUserApi();
  const { household } = useHouseholdSelf();
  const loading = ref(false);

  let queryFilter = "";
  const { $auth, i18n } = useContext();
  if (onlyMine) {
    queryFilter = `householdId = "${$auth.user?.householdId || ""}"`;
  }

  const actions = {
    getAll() {
      loading.value = true;
      const units = useAsync(async () => {
        const { data } = await api.cookbooks.getAll(1, -1, { orderBy: "position", orderDirection: "asc", queryFilter });

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
      const { data } = await api.cookbooks.getAll(1, -1, { orderBy: "position", orderDirection: "asc", queryFilter });

      if (data && data.items && store.ref?.value) {
        store.ref.value = data.items;
      }

      loading.value = false;
    },
    async createOne() {
      loading.value = true;
      const { data } = await api.cookbooks.createOne({
        name: i18n.t("cookbook.household-cookbook-name", [household.value?.name || "", String((store.ref?.value?.length ?? 0) + 1)]) as string,
        position: (store.ref?.value?.length ?? 0) + 1,
        queryFilterString: "",
      });
      if (data && store.ref?.value) {
        store.ref.value.push(data);
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
      if (data && store.ref?.value) {
        this.refreshAll();
      }
      loading.value = false;
      return data;
    },

    async updateOrder() {
      if (!store.ref?.value) {
        return;
      }

      loading.value = true;

      store.ref.value.forEach((element, index) => {
        element.position = index + 1;
      });

      const { data } = await api.cookbooks.updateAll(store.ref.value);

      if (data && store.ref.value) {
        this.refreshAll();
      }

      loading.value = true;
    },
    async deleteOne(id: string | number) {
      loading.value = true;
      const { data } = await api.cookbooks.deleteOne(id);
      if (data && store.ref?.value) {
        this.refreshAll();
      }
    },
    flushStore() {
      store.ref = null;
    },
  };

  if (!store.ref) {
    store.ref = actions.getAll();
  }

  return { cookbooks: store.ref, actions };
}

export const useCookbooks = function () {
  return useCookbooksFactory(cookbookStore);
};

export const useMyCookbooks = function () {
  return useCookbooksFactory(myCookbookStore, true);
}
