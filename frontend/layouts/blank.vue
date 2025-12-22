<template>
  <v-app dark>
    <TheSnackbar />

    <v-banner
      v-if="$appInfo.demoStatus"
      sticky
    >
      <div class="text-center">
        <b> {{ $t("demo.info_message_with_version", { version: $appInfo.version }) }} </b>
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

export default defineNuxtComponent({
  components: { TheSnackbar },
});
</script>
