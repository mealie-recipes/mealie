<template>
  <div />
</template>

<script lang="ts">
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
        if (!isDemo && isFirstLogin && $auth.user.value?.admin) {
          router.push("/admin/setup");
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
