import { useAsync, ref, reactive, Ref } from "@nuxtjs/composition-api";
import { useAsyncKey } from "../use-utils";
import { useUserApi } from "~/composables/api";
import { Unit } from "~/api/class-interfaces/recipe-units";
import { VForm } from "~/types/vuetify";

let unitStore: Ref<Unit[] | null> | null = null;

export const useUnits = function () {
  const api = useUserApi();
  const loading = ref(false);
  const deleteTargetId = ref(0);
  const validForm = ref(true);

  const workingUnitData = reactive({
    id: 0,
    name: "",
    fraction: true,
    abbreviation: "",
    description: "",
  });

  const actions = {
    getAll() {
      loading.value = true;
      const units = useAsync(async () => {
        const { data } = await api.units.getAll();
        return data;
      }, useAsyncKey());

      loading.value = false;
      return units;
    },
    async refreshAll() {
      loading.value = true;
      const { data } = await api.units.getAll();

      if (data && unitStore) {
        unitStore.value = data;
      }

      loading.value = false;
    },
    async createOne(domForm: VForm | null = null) {
      if (domForm && !domForm.validate()) {
        validForm.value = false;
        return;
      }

      loading.value = true;
      const { data } = await api.units.createOne(workingUnitData);
      if (data && unitStore?.value) {
        unitStore.value.push(data);
      } else {
        this.refreshAll();
      }
      domForm?.reset();
      validForm.value = true;
      this.resetWorking();
      loading.value = false;
    },
    async updateOne() {
      if (!workingUnitData.id) {
        return;
      }

      loading.value = true;
      const { data } = await api.units.updateOne(workingUnitData.id, workingUnitData);
      if (data && unitStore?.value) {
        this.refreshAll();
      }
      loading.value = false;
    },
    async deleteOne(id: string | number) {
      loading.value = true;
      const { data } = await api.units.deleteOne(id);
      if (data && unitStore?.value) {
        this.refreshAll();
      }
    },
    resetWorking() {
      workingUnitData.id = 0;
      workingUnitData.name = "";
      workingUnitData.abbreviation = "";
      workingUnitData.description = "";
    },
    setWorking(item: Unit) {
      workingUnitData.id = item.id;
      workingUnitData.name = item.name;
      workingUnitData.fraction = item.fraction;
      workingUnitData.abbreviation = item.abbreviation;
      workingUnitData.description = item.description;
    },
    flushStore() {
      unitStore = null;
    },
  };

  if (!unitStore) {
    unitStore = actions.getAll();
  }

  return { units: unitStore, workingUnitData, deleteTargetId, actions, validForm };
};
