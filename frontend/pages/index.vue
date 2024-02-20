<template>
  <div></div>
</template>

<script lang="ts">
import { computed, defineComponent, useAsync, useContext, useRouter } from "@nuxtjs/composition-api";
import { useAsyncKey } from "~/composables/use-utils";
import { AppInfo, AppStartupInfo } from "~/lib/api/types/admin";

export default defineComponent({
  layout: "blank",
  setup() {
    const { $auth, $axios } = useContext();
    const router = useRouter();
    const groupSlug = computed(() => $auth.user?.groupSlug);

    async function redirectPublicUserToDefaultGroup() {
      const { data } = await $axios.get<AppInfo>("/api/app/about");
      if (data?.defaultGroupSlug) {
        router.push(`/g/${data.defaultGroupSlug}`);
      } else {
        router.push("/login");
      }
    }

    useAsync(async () => {
      if (groupSlug.value) {
        const data = await $axios.get<AppStartupInfo>("/api/app/about/startup-info");
        const isDemo = data.data.isDemo;
        const isFirstLogin = data.data.isFirstLogin;
        if (!isDemo && isFirstLogin && $auth.user?.admin) {
          router.push("/admin/setup");
        } else {
          router.push(`/g/${groupSlug.value}`);
        }
      } else {
        redirectPublicUserToDefaultGroup();
      }
    }, useAsyncKey());
  }
});
</script>
