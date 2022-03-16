import { Ref, useAsync } from "@nuxtjs/composition-api";
import { useAsyncKey } from "../use-utils";
import { AppInfo } from "~/types/api-types/admin";

export function useAppInfo(): Ref<AppInfo | null> {
  return useAsync(async () => {
    // We use fetch here to reduce need for additional dependencies
    const data = await fetch("/api/app/about").then((res) => res.json());
    return data as AppInfo;
  }, useAsyncKey());
}
