import { reactive, ref, Ref } from "@nuxtjs/composition-api";
import { useStoreActions } from "../partials/use-actions-factory";
import { MultiPurposeLabelOut } from "~/lib/api/types/labels";
import { useUserApi } from "~/composables/api";

let labelStore: Ref<MultiPurposeLabelOut[] | null> | null = null;

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
  const loading = ref(false);

  const actions = {
    ...useStoreActions<MultiPurposeLabelOut>(api.multiPurposeLabels, labelStore, loading),
    flushStore() {
      labelStore = null;
    },
  };

  if (!labelStore) {
    labelStore = actions.getAll();
  }

  return {
    labels: labelStore,
    actions,
    loading,
  };
}
