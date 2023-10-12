<template>
</template>

<script lang="ts">
import { defineComponent, useContext, useRouter } from "@nuxtjs/composition-api";
import DefaultLayout from "@/components/Layout/DefaultLayout.vue";

export default defineComponent({
  components: { DefaultLayout },
  setup() {
    const { $auth } = useContext();
    const router = useRouter();

    if (!$auth.loggedIn) {
      router.push("/login");
    }
  }
});
</script>
