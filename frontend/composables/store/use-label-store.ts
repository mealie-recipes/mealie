import type { Composer } from "vue-i18n";
import { useData, useStore } from "../partials/use-store-factory";
import type { MultiPurposeLabelOut } from "~/lib/api/types/labels";
import { useUserApi } from "~/composables/api";

const store: Ref<MultiPurposeLabelOut[]> = ref([]);
const loading = ref(false);

export function resetLabelStore() {
  store.value = [];
  loading.value = false;
}

export const useLabelData = function () {
  return useData<MultiPurposeLabelOut>({
    groupId: "",
    id: "",
    name: "",
    color: "",
  });
};

export const useLabelStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  return useStore<MultiPurposeLabelOut>("label", store, loading, api.multiPurposeLabels);
};
