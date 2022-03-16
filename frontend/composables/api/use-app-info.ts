import { onMounted, ref, Ref } from "@nuxtjs/composition-api";
import { AppInfo } from "~/types/api-types/admin";

export function useAppInfo(): Ref<AppInfo | null> {
  const appInfo = ref<null | AppInfo>(null);

  onMounted(async () => {
    const data = await fetch("/api/app/about").then((res) => res.json());
    appInfo.value = data as AppInfo;
  });

  return appInfo;
}
