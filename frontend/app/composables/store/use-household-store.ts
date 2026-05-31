import type { Composer } from "vue-i18n";
import { useReadOnlyStore } from "../partials/use-store-factory";
import type { HouseholdSummary } from "~/lib/api/types/household";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<HouseholdSummary[]> = ref([]);
const loading = ref(false);
const initialized = ref(false);
const publicLoading = ref(false);
const publicInitialized = ref(false);

export function resetHouseholdStore() {
  store.value = [];
  loading.value = false;
  initialized.value = false;
  publicLoading.value = false;
  publicInitialized.value = false;
}

export const useHouseholdStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  return useReadOnlyStore<HouseholdSummary>("household", store, loading, initialized, api.households);
};

export const usePublicHouseholdStore = function (groupSlug: string, i18n?: Composer) {
  const api = usePublicExploreApi(groupSlug, i18n).explore;
  return useReadOnlyStore<HouseholdSummary>("household-public", store, publicLoading, publicInitialized, api.households);
};
