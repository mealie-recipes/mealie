import { Ref, useAsync } from "@nuxtjs/composition-api";
import { useAsyncKey } from "../use-utils";
import { BaseCRUDAPI } from "~/api/_base";

type BoundT = {
  id: string | number;
};

interface StoreActions<T extends BoundT> {
  getAll(): Ref<T[] | null>;
  refresh(): Promise<void>;
  createOne(createData: T): Promise<void>;
  updateOne(updateData: T): Promise<void>;
  deleteOne(id: string | number): Promise<void>;
}

/**
 * useStoreActions is a factory function that returns a set of methods
 * that can be reused to manage the state of a data store without using
 * Vuex. This is primarily used for basic CRUD operations that required
 * a lot of refreshing hooks to be called on operations
 */
export function useStoreActions<T extends BoundT>(
  api: BaseCRUDAPI<unknown, T, unknown>,
  allRef: Ref<T[] | null> | null,
  loading: Ref<boolean>
): StoreActions<T> {
  function getAll() {
    loading.value = true;
    const allItems = useAsync(async () => {
      const { data } = await api.getAll();
      return data;
    }, useAsyncKey());

    loading.value = false;
    return allItems;
  }

  async function refresh() {
    loading.value = true;
    const { data } = await api.getAll();

    if (data && allRef) {
      allRef.value = data;
    }

    loading.value = false;
  }

  async function createOne(createData: T) {
    loading.value = true;
    const { data } = await api.createOne(createData);
    if (data && allRef?.value) {
      allRef.value.push(data);
    } else {
      refresh();
    }
    loading.value = false;
  }

  async function updateOne(updateData: T) {
    if (!updateData.id) {
      return;
    }

    loading.value = true;
    const { data } = await api.updateOne(updateData.id, updateData);
    if (data && allRef?.value) {
      refresh();
    }
    loading.value = false;
  }

  async function deleteOne(id: string | number) {
    loading.value = true;
    const { data } = await api.deleteOne(id);
    if (data && allRef?.value) {
      refresh();
    }
    loading.value = false;
  }

  return {
    getAll,
    refresh,
    createOne,
    updateOne,
    deleteOne,
  };
}
