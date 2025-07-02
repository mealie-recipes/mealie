<template>
  <v-app dark>
    <NuxtPwaManifest />
    <TheSnackbar />

    <v-banner
      v-if="isDemo"
      sticky
    >
      <div class="text-center">
        <b> {{ $t("demo.info_message_with_version", { version: version }) }} </b>
      </div>
    </v-banner>

    <v-main>
      <v-scroll-x-transition>
        <div>
          <NuxtPage />
        </div>
      </v-scroll-x-transition>
    </v-main>
  </v-app>
</template>

<script lang="ts">
import TheSnackbar from "~/components/Layout/LayoutParts/TheSnackbar.vue";
import { useAppInfo } from "~/composables/api";

export default defineNuxtComponent({
  components: { TheSnackbar },
  setup() {
    const appInfo = useAppInfo();

    const isDemo = computed(() => appInfo?.value?.demoStatus || false);

    const i18n = useI18n();
    const version = computed(() => appInfo?.value?.version || i18n.t("about.unknown-version"));

    return {
      appInfo,
      isDemo,
      version,
    };
  },
});
</script>
