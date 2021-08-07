import { useAsync, ref } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";
import { CreateGroup } from "~/api/class-interfaces/groups";



export const useGroups = function () {
  const api = useApiSingleton();
  const loading = ref(false);

  function getAllGroups() {
    loading.value = true;
    const asyncKey = String(Date.now());
    const groups = useAsync(async () => {
      const { data } = await api.groups.getAll();
      return data;
    }, asyncKey);

    loading.value = false;
    return groups;
  }

  async function refreshAllGroups() {
    loading.value = true;
    const { data } = await api.groups.getAll();
    groups.value = data;
    loading.value = false;
  }

  async function deleteGroup(id: string | number) {
    loading.value = true;
    const { data } = await api.groups.deleteOne(id);
    loading.value = false;
    refreshAllGroups();
    return data;
  }

  async function createGroup(payload: CreateGroup) {
    console.log(payload);
    loading.value = true;
    const { data } = await api.groups.createOne(payload);

    if (data && groups.value) {
      groups.value.push(data);
    }
  }

  const groups = getAllGroups();

  return { groups, getAllGroups, refreshAllGroups, deleteGroup, createGroup };
};
