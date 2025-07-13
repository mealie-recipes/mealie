import { useAdminApi, useUserApi } from "~/composables/api";
import type { HouseholdCreate, HouseholdInDB } from "~/lib/api/types/household";

const householdSelfRef = ref<HouseholdInDB | null>(null);
const loading = ref(false);

export const useHouseholdSelf = function () {
  const api = useUserApi();

  async function refreshHouseholdSelf() {
    loading.value = true;
    const { data } = await api.households.getCurrentUserHousehold();
    householdSelfRef.value = data;
    loading.value = false;
  }

  const actions = {
    get() {
      if (!(householdSelfRef.value || loading.value)) {
        refreshHouseholdSelf();
      }

      return householdSelfRef;
    },
    async updatePreferences() {
      if (!householdSelfRef.value) {
        await refreshHouseholdSelf();
      }
      if (!householdSelfRef.value?.preferences) {
        return;
      }

      const { data } = await api.households.setPreferences(householdSelfRef.value.preferences);

      if (data) {
        householdSelfRef.value.preferences = data;
      }

      return data || undefined;
    },
  };

  const household = actions.get();

  return { actions, household };
};

export const useAdminHouseholds = function () {
  const api = useAdminApi();
  const loading = ref(false);
  const households = ref<HouseholdInDB[] | null>(null);

  async function getAllHouseholds() {
    loading.value = true;
    const { data } = await api.households.getAll(1, -1, { orderBy: "name, group.name", orderDirection: "asc" });

    if (data) {
      households.value = data.items;
    }
    else {
      households.value = null;
    }

    loading.value = false;
  }

  async function refreshAllHouseholds() {
    await getAllHouseholds();
  }

  async function deleteHousehold(id: string | number) {
    loading.value = true;
    const { data } = await api.households.deleteOne(id);
    loading.value = false;
    await refreshAllHouseholds();
    return data;
  }

  async function createHousehold(payload: HouseholdCreate) {
    loading.value = true;
    const { data } = await api.households.createOne(payload);

    if (data && households.value) {
      households.value.push(data);
    }
    loading.value = false;
  }

  function useHouseholdsInGroup(groupIdRef: Ref<string>) {
    return computed(
      () => {
        return (households.value && groupIdRef.value)
          ? households.value.filter(h => h.groupId === groupIdRef.value)
          : [];
      },
    );
  }

  if (!households.value) {
    getAllHouseholds();
  }

  return {
    households,
    useHouseholdsInGroup,
    getAllHouseholds,
    refreshAllHouseholds,
    deleteHousehold,
    createHousehold,
  };
};
