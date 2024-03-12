import { reactive, ref, Ref } from "@nuxtjs/composition-api";
import { useStoreActions } from "../partials/use-actions-factory";
import { MultiPurposeLabelOut } from "~/lib/api/types/labels";
import { useUserApi } from "~/composables/api";

let labelStore: Ref<MultiPurposeLabelOut[] | null> = ref([]);
const storeLoading = ref(false);

export function useLabelData() {
  const data = reactive({
    groupId: "",
    id: "",
    name: "",
    color: "",
  });

  function reset() {
    data.groupId = "";
    data.id = "";
    data.name = "";
    data.color = "";
  }

  return {
    data,
    reset,
  };
}

export function useLabelStore() {
  const api = useUserApi();
  const loading = storeLoading;

  const actions = {
    ...useStoreActions<MultiPurposeLabelOut>(api.multiPurposeLabels, labelStore, loading),
    flushStore() {
      labelStore.value = [];
    },
  };

  if (!loading.value && (!labelStore.value || labelStore.value?.length === 0)) {
    labelStore = actions.getAll();
  }

  return {
    labels: labelStore,
    actions,
    loading,
  };
}
