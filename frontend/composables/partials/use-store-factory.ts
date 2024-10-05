import { ref, reactive, Ref } from "@nuxtjs/composition-api";
import { useReadOnlyActions, useStoreActions } from "./use-actions-factory";
import { BoundT } from "./types";
import { BaseCRUDAPI, BaseCRUDAPIReadOnly } from "~/lib/api/base/base-clients";
import { QueryValue } from "~/lib/api/base/route";

export const useData = function<T extends BoundT>(defaultObject: T) {
  const data = reactive({ ...defaultObject });
  function reset() {
    Object.assign(data, defaultObject);
  };

  return { data, reset };
}

export const useReadOnlyStore = function<T extends BoundT>(
  store: Ref<T[]>,
  loading: Ref<boolean>,
  api: BaseCRUDAPIReadOnly<T>,
  params = {} as Record<string, QueryValue>,
) {
  const storeActions = useReadOnlyActions(api, store, loading);
  const actions = {
    ...storeActions,
    async refresh() {
      return await storeActions.refresh(1, -1, params);
    },
    flushStore() {
      store.value = [];
    },
  };

  if (!loading.value && (!store.value || store.value.length === 0)) {
    const result = actions.getAll(1, -1, params);
    store.value = result.value || [];
  }

  return { store, actions };
}

export const useStore = function<T extends BoundT>(
  store: Ref<T[]>,
  loading: Ref<boolean>,
  api: BaseCRUDAPI<unknown, T, unknown>,
  params = {} as Record<string, QueryValue>,
) {
  const storeActions = useStoreActions(api, store, loading);
  const actions = {
    ...storeActions,
    async refresh() {
      return await storeActions.refresh(1, -1, params);
    },
    flushStore() {
      store = ref([]);
    },
  };

  if (!loading.value && (!store.value || store.value.length === 0)) {
    const result = actions.getAll(1, -1, params);
    store.value = result.value || [];
  }

  return { store, actions };
}
