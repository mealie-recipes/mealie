<template>
  <div></div>
</template>

<script lang="ts">
import { computed, defineComponent, useContext, useRouter } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";

export default defineComponent({
  layout: "blank",
  async setup() {
    const { $auth } = useContext();
    const router = useRouter();

    const api = useUserApi();
    if ($auth.user?.iss) {
      // this is oidc, get the user from the server and set it
      const { data } = await api.users.getSelf();
      $auth.setUser(data);
    }

    const groupSlug = computed(() => $auth.user?.groupSlug);

    if (groupSlug.value) {
      router.push(`/g/${groupSlug.value}`);
    } else {
      router.push("/login");
    }
  }
});
</script>
