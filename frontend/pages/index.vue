<template>
  <div></div>
</template>

<script lang="ts">
import { computed, defineComponent, useContext, useRouter } from "@nuxtjs/composition-api";
import { AppInfo } from "~/lib/api/types/admin";

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

    if (groupSlug.value) {
      router.push(`/g/${groupSlug.value}`);
    } else {
      redirectPublicUserToDefaultGroup();
    }
  }
});
</script>
