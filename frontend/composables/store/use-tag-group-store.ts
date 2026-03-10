import type { Composer } from "vue-i18n";
import { useData, useReadOnlyStore, useStore } from "../partials/use-store-factory";
import type { TagGroupOut } from "~/lib/api/types/recipe";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<TagGroupOut[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export function resetTagGroupStore() {
  store.value = [];
  loading.value = false;
  publicLoading.value = false;
}

export const useTagGroupData = function () {
  return useData<TagGroupOut>({
    id: "",
    groupId: "",
    name: "",
    slug: "",
    color: null,
    position: 0,
  });
};

export const useTagGroupStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  return useStore<TagGroupOut>("tagGroup", store, loading, api.tagGroups);
};

export const usePublicTagGroupStore = function (groupSlug: string, i18n?: Composer) {
  const api = usePublicExploreApi(groupSlug, i18n).explore;
  return useReadOnlyStore<TagGroupOut>("tagGroup", store, publicLoading, api.tagGroups);
};
