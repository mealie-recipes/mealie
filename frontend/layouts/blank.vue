<template>
  <v-app dark>
    <TheSnackbar />

    <v-banner v-if="isDemo" sticky>
      <div class="text-center">
        <b> {{ $t("demo.info_message_with_version", { version: version }) }} </b> |
        {{ $t("demo.demo_username", { username: "changeme@email.com" }) }} |
        {{ $t("demo.demo_password", { password: "demo" }) }}
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
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import TheSnackbar from "~/components/Layout/TheSnackbar.vue";
import { useAppInfo } from "~/composables/api";
export default defineComponent({
  components: { TheSnackbar },
  setup() {
    const appInfo = useAppInfo();

    const isDemo = computed(() => appInfo?.value?.demoStatus || false);

    const { i18n } = useContext();
    const version = computed(() => appInfo?.value?.version || i18n.t("about.unknown-version"));

    return {
      appInfo,
      isDemo,
      version,
    };
  },
});
</script>
