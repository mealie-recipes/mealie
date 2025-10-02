import type { AppInfo } from "~/lib/api/types/admin";

export function useAppInfo(): Ref<AppInfo | null> {
  const i18n = useI18n();
  const { $axios } = useNuxtApp();
  $axios.defaults.headers.common["Accept-Language"] = i18n.locale.value;

  const { data: appInfo } = useAsyncData("app-info", async () => {
    const data = await $axios.get<AppInfo>("/api/app/about");
    return data.data;
  });

  return appInfo;
}
