import { useAsync, ref } from "@nuxtjs/composition-api";
import { useAsyncKey } from "./use-utils";
import { useApiSingleton } from "~/composables/use-api";
import { GroupWebhook } from "~/api/class-interfaces/group-webhooks";

export const useGroupWebhooks = function () {
  const api = useApiSingleton();
  const loading = ref(false);
  const validForm = ref(true);

  const actions = {
    getAll() {
      loading.value = true;
      const units = useAsync(async () => {
        const { data } = await api.groupWebhooks.getAll();

        return data;
      }, useAsyncKey());

      loading.value = false;
      return units;
    },
    async refreshAll() {
      loading.value = true;
      const { data } = await api.groupWebhooks.getAll();

      if (data) {
        webhooks.value = data;
      }

      loading.value = false;
    },
    async createOne() {
      loading.value = true;

      const payload = {
        enabled: false,
        name: "New Webhook",
        url: "",
        time: "00:00",
      };

      const { data } = await api.groupWebhooks.createOne(payload);
      if (data) {
        this.refreshAll();
      }

      loading.value = false;
    },
    async updateOne(updateData: GroupWebhook) {
      if (!updateData.id) {
        return;
      }

      loading.value = true;
      const { data } = await api.groupWebhooks.updateOne(updateData.id, updateData);
      if (data) {
        this.refreshAll();
      }
      loading.value = false;
    },

    async deleteOne(id: string | number) {
      loading.value = true;
      const { data } = await api.groupWebhooks.deleteOne(id);
      if (data) {
        this.refreshAll();
      }
    },
  };

  const webhooks = actions.getAll();

  return { webhooks, actions, validForm };
};
