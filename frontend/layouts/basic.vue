<template>
  <v-app dark>
    <NuxtPwaManifest />
    <TheSnackbar />

    <AppHeader :menu="false" />
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
import AppHeader from "@/components/Layout/LayoutParts/AppHeader.vue";

export default defineNuxtComponent({
  components: { TheSnackbar, AppHeader },
});
</script>
