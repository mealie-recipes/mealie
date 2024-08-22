import { useAsync, ref } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { GroupBase, GroupSummary } from "~/lib/api/types/user";

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

  function getAllGroups() {
    loading.value = true;
    const asyncKey = String(Date.now());
    const groups = useAsync(async () => {
      const { data } = await api.groups.getAll(1, -1, {orderBy: "name", orderDirection: "asc"});;

      if (data) {
        return data.items;
      } else {
        return null;
      }
    }, asyncKey);

    loading.value = false;
    return groups;
  }

  async function refreshAllGroups() {
    loading.value = true;
    const { data } = await api.groups.getAll(1, -1, {orderBy: "name", orderDirection: "asc"});;

    if (data) {
      groups.value = data.items;
    } else {
      groups.value = null;
    }

    loading.value = false;
  }

  async function deleteGroup(id: string | number) {
    loading.value = true;
    const { data } = await api.groups.deleteOne(id);
    loading.value = false;
    refreshAllGroups();
    return data;
  }

  async function createGroup(payload: GroupBase) {
    loading.value = true;
    const { data } = await api.groups.createOne(payload);

    if (data && groups.value) {
      groups.value.push(data);
    }
  }

  const groups = getAllGroups();

  return { groups, getAllGroups, refreshAllGroups, deleteGroup, createGroup };
};
