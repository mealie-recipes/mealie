import { ref, reactive, Ref } from "@nuxtjs/composition-api";
import { useReadOnlyActions, useStoreActions } from "./use-actions-factory";
import { BoundT } from "./types";
import { BaseCRUDAPI, BaseCRUDAPIReadOnly } from "~/lib/api/base/base-clients";

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
) {
  const actions = {
    ...useReadOnlyActions(api, store, loading),
    flushStore() {
      store.value = [];
    },
  };

  if (!loading.value && (!store.value || store.value.length === 0)) {
    const result = actions.getAll();
    store.value = result.value || [];
  }

  return { store, actions };
}

export const useStore = function<T extends BoundT>(
  store: Ref<T[]>,
  loading: Ref<boolean>,
  api: BaseCRUDAPI<unknown, T, unknown>,
) {
  const actions = {
    ...useStoreActions(api, store, loading),
    flushStore() {
      store = ref([]);
    },
  };

  if (!loading.value && (!store.value || store.value.length === 0)) {
    const result = actions.getAll();
    store.value = result.value || [];
  }

  return { store, actions };
}
