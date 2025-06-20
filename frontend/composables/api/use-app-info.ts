import { useAsyncKey } from "../use-utils";
import type { AppInfo } from "~/lib/api/types/admin";

export function useAppInfo(): Ref<AppInfo | null> {
  const appInfo = ref<null | AppInfo>(null);

  const i18n = useI18n();
  const { $axios } = useNuxtApp();
  $axios.defaults.headers.common["Accept-Language"] = i18n.locale.value;

  useAsyncData(useAsyncKey(), async () => {
    const data = await $axios.get<AppInfo>("/api/app/about");
    appInfo.value = data.data;
  });

  return appInfo;
}
