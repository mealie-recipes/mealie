import { useAsync, ref } from "@nuxtjs/composition-api";
import { CreateEventNotification } from "@/api/class-interfaces/event-notifications";
import { useAsyncKey } from "./use-utils";
import { useApiSingleton } from "~/composables/use-api";

const notificationTypes = ["General", "Discord", "Gotify", "Pushover", "Home Assistant"];


export const useNotifications = function () {
  const api = useApiSingleton();
  const loading = ref(false);

  const createNotificationData = ref<CreateEventNotification>({
    name: "",
    type: "General",
    general: true,
    recipe: true,
    backup: true,
    scheduled: true,
    migration: true,
    group: true,
    user: true,
    notificationUrl: "",
  });

  const deleteTarget = ref(0)

  function getNotifications() {
    loading.value = true;
    const notifications = useAsync(async () => {
      const { data } = await api.notifications.getAll();
      return data;
    }, useAsyncKey());
    loading.value = false;
    return notifications;
  }

  async function refreshNotifications() {
    loading.value = true;
    const { data } = await api.notifications.getAll();
    if (data) {
      notifications.value = data;
    }
    loading.value = false;
  }

  async function createNotification() {
    if (createNotificationData.value.name === "" || createNotificationData.value.notificationUrl === "") {
      return;
    }
    const { response } = await api.notifications.createOne(createNotificationData.value);

    if (response?.status === 200) {
      refreshNotifications();
    }
  }

  async function deleteNotification() {
    const { response } = await api.notifications.deleteOne(deleteTarget.value);
    if (response?.status === 200) {
      refreshNotifications();
    }
  }

  async function testById(id: number) {
    const {data} = await api.notifications.testNotification(id, null)
    console.log(data)
  }

  async function testByUrl(testUrl: string) {
    const {data} = await api.notifications.testNotification(null, testUrl)
    console.log(data)
  }

  const notifications = getNotifications();

  return {
    createNotification,
    deleteNotification,
    refreshNotifications,
    getNotifications,
    testById,
    testByUrl,
    notifications,
    loading,
    createNotificationData,
    notificationTypes,
    deleteTarget,
  };
};
