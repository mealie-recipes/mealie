<template>
  <v-app dark>
    <TheSnackbar />

    <v-banner v-if="isDemo" sticky>
      <div class="text-center">
        <b> This is a Demo for version: {{ version }} </b> | Username: changeme@email.com | Password: demo
      </div>
    </v-banner>

    <v-main>
      <v-scroll-x-transition>
        <Nuxt />
      </v-scroll-x-transition>
    </v-main>
  </v-app>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import TheSnackbar from "~/components/Layout/TheSnackbar.vue";
import { useAppInfo } from "~/composables/api";
export default defineComponent({
  components: { TheSnackbar },
  setup() {
    const appInfo = useAppInfo();

    const isDemo = computed(() => appInfo?.value?.demoStatus || false);

    const version = computed(() => appInfo?.value?.version || "unknown");

    return {
      appInfo,
      isDemo,
      version,
    };
  },
});
</script>
