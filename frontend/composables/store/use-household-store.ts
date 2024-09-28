import { ref, Ref } from "@nuxtjs/composition-api";
import { useReadOnlyStore } from "../partials/use-store-factory";
import { HouseholdSummary } from "~/lib/api/types/household";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<HouseholdSummary[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export const useHouseholdStore = function () {
  const api = useUserApi();
  return useReadOnlyStore<HouseholdSummary>(store, loading, api.households);
}

export const usePublicHouseholdStore = function (groupSlug: string) {
  const api = usePublicExploreApi(groupSlug).explore;
  return useReadOnlyStore<HouseholdSummary>(store, publicLoading, api.households);
}
