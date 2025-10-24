<template>
  <div />
</template>

<script lang="ts">
import useDefaultActivity from "~/composables/use-default-activity";
import { useUserActivityPreferences } from "~/composables/use-users/preferences";
import { useAsyncKey } from "~/composables/use-utils";
import type { AppInfo, AppStartupInfo } from "~/lib/api/types/admin";

export default defineNuxtComponent({
  setup() {
    definePageMeta({
      layout: "blank",
    });

    const $auth = useMealieAuth();
    const { $axios } = useNuxtApp();
    const router = useRouter();
    const activityPreferences = useUserActivityPreferences();
    const { getDefaultActivityRoute } = useDefaultActivity();
    const groupSlug = computed(() => $auth.user.value?.groupSlug);

    async function redirectPublicUserToDefaultGroup() {
      const { data } = await $axios.get<AppInfo>("/api/app/about");
      if (data?.defaultGroupSlug) {
        router.push(`/g/${data.defaultGroupSlug}`);
      }
      else {
        router.push("/login");
      }
    }

    useAsyncData(useAsyncKey(), async () => {
      if (groupSlug.value) {
        const data = await $axios.get<AppStartupInfo>("/api/app/about/startup-info");
        const isDemo = data.data.isDemo;
        const isFirstLogin = data.data.isFirstLogin;
        const defaultActivityRoute = getDefaultActivityRoute(
          activityPreferences.value.defaultActivity,
          groupSlug.value,
        );
        if (!isDemo && isFirstLogin && $auth.user.value?.admin) {
          router.push("/admin/setup");
        }
        else if (defaultActivityRoute) {
          router.push(defaultActivityRoute);
        }
        else {
          router.push(`/g/${groupSlug.value}`);
        }
      }
      else {
        redirectPublicUserToDefaultGroup();
      }
    });
  },
});
</script>
