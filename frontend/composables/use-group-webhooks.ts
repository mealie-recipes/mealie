import { useAsync, ref } from "@nuxtjs/composition-api";
import { useAsyncKey } from "./use-utils";
import { useUserApi } from "~/composables/api";
import { ReadWebhook } from "~/lib/api/types/group";

export const useGroupWebhooks = function () {
  const api = useUserApi();
  const loading = ref(false);
  const validForm = ref(true);

  const actions = {
    getAll() {
      loading.value = true;
      const units = useAsync(async () => {
        const { data } = await api.groupWebhooks.getAll();

        if (data) {
          return data.items;
        } else {
          return null;
        }
      }, useAsyncKey());

      loading.value = false;
      return units;
    },
    async refreshAll() {
      loading.value = true;
      const { data } = await api.groupWebhooks.getAll();

      if (data && data.items) {
        webhooks.value = data.items;
      }

      loading.value = false;
    },
    async createOne() {
      loading.value = true;

      const payload = {
        enabled: false,
        name: "New Webhook",
        url: "",
        scheduledTime: "00:00",
      };

      const { data } = await api.groupWebhooks.createOne(payload);
      if (data) {
        this.refreshAll();
      }

      loading.value = false;
    },
    async updateOne(updateData: ReadWebhook) {
      if (!updateData.id) {
        return;
      }

      // Convert to UTC time
      const [hours, minutes] = updateData.scheduledTime.split(":");

      const newDt = new Date();
      newDt.setHours(Number(hours));
      newDt.setMinutes(Number(minutes));

      updateData.scheduledTime = `${pad(newDt.getUTCHours(), 2)}:${pad(newDt.getUTCMinutes(), 2)}`;
      console.log(updateData.scheduledTime);

      const payload = {
        ...updateData,
        scheduledTime: updateData.scheduledTime,
      };

      loading.value = true;
      const { data } = await api.groupWebhooks.updateOne(updateData.id, payload);
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

function pad(num: number, size: number) {
  let numStr = num.toString();
  while (numStr.length < size) numStr = "0" + numStr;
  return numStr;
}

export function timeUTCToLocal(time: string): string {
  const [hours, minutes] = time.split(":");
  const dt = new Date();
  dt.setUTCMinutes(Number(minutes));
  dt.setUTCHours(Number(hours));
  return `${pad(dt.getHours(), 2)}:${pad(dt.getMinutes(), 2)}`;
}

export function timeLocalToUTC(time: string) {
  const [hours, minutes] = time.split(":");
  const dt = new Date();
  dt.setHours(Number(hours));
  dt.setMinutes(Number(minutes));
  return `${pad(dt.getUTCHours(), 2)}:${pad(dt.getUTCMinutes(), 2)}`;
}
