<template>
  <div></div>
</template>

<script lang="ts">
import { computed, defineComponent, useContext, useRouter } from "@nuxtjs/composition-api";
export default defineComponent({
  layout: "blank",
  setup() {
    const { $auth } = useContext();
    const router = useRouter();
    const groupSlug = computed(() => $auth.user?.groupSlug);

    if (groupSlug.value) {
      router.push(`/g/${groupSlug.value}`);
    } else {
      router.push("/login");
    }
  }
});
</script>
