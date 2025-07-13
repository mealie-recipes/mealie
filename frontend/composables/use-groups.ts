import { useUserApi } from "~/composables/api";
import type { GroupBase, GroupSummary } from "~/lib/api/types/user";

const groupSelfRef = ref<GroupSummary | null>(null);
const loading = ref(false);

export const useGroupSelf = function () {
  const api = useUserApi();
  async function refreshGroupSelf() {
    loading.value = true;
    const { data } = await api.groups.getCurrentUserGroup();
    groupSelfRef.value = data;
    loading.value = false;
  }

  const actions = {
    get() {
      if (!(groupSelfRef.value || loading.value)) {
        refreshGroupSelf();
      }

      return groupSelfRef;
    },
    async updatePreferences() {
      if (!groupSelfRef.value) {
        await refreshGroupSelf();
      }
      if (!groupSelfRef.value?.preferences) {
        return;
      }

      const { data } = await api.groups.setPreferences(groupSelfRef.value.preferences);

      if (data) {
        groupSelfRef.value.preferences = data;
      }
    },
  };

  const group = actions.get();

  return { actions, group };
};

export const useGroups = function () {
  const api = useUserApi();
  const loading = ref(false);
  const groups = ref<GroupSummary[] | null>(null);

  async function getAllGroups() {
    loading.value = true;
    const { data } = await api.groups.getAll(1, -1, { orderBy: "name", orderDirection: "asc" });

    if (data) {
      groups.value = data.items;
    }
    else {
      groups.value = null;
    }

    loading.value = false;
  }

  async function refreshAllGroups() {
    await getAllGroups();
  }

  async function deleteGroup(id: string | number) {
    loading.value = true;
    const { data } = await api.groups.deleteOne(id);
    loading.value = false;
    await refreshAllGroups();
    return data;
  }

  async function createGroup(payload: GroupBase) {
    loading.value = true;
    const { data } = await api.groups.createOne(payload);

    if (data && groups.value) {
      groups.value.push(data);
    }
    loading.value = false;
  }

  // Initialize data on first call
  if (!groups.value) {
    getAllGroups();
  }

  return { groups, getAllGroups, refreshAllGroups, deleteGroup, createGroup };
};
