import type { Composer } from "vue-i18n";
import { useReadOnlyStore } from "../partials/use-store-factory";
import type { HouseholdSummary } from "~/lib/api/types/household";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<HouseholdSummary[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export function resetHouseholdStore() {
  store.value = [];
  loading.value = false;
  publicLoading.value = false;
}

export const useHouseholdStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  return useReadOnlyStore<HouseholdSummary>("household", store, loading, api.households);
};

export const usePublicHouseholdStore = function (groupSlug: string, i18n?: Composer) {
  const api = usePublicExploreApi(groupSlug, i18n).explore;
  return useReadOnlyStore<HouseholdSummary>("household-public", store, publicLoading, api.households);
};
