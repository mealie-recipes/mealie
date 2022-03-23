import { ref, Ref, useAsync, useContext } from "@nuxtjs/composition-api";
import { useAsyncKey } from "../use-utils";
import { AppInfo } from "~/types/api-types/admin";

export function useAppInfo(): Ref<AppInfo | null> {
  const appInfo = ref<null | AppInfo>(null);

  const { $axios } = useContext();

  useAsync(async () => {
    const data = await $axios.get<AppInfo>("/api/app/about");
    appInfo.value = data.data;
  }, useAsyncKey());

  return appInfo;
}
