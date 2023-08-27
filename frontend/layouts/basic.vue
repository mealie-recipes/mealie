<template>
  <v-app dark>
    <TheSnackbar />

    <AppHeader :menu="false"> </AppHeader>
    <v-main>
      <v-scroll-x-transition>
        <Nuxt />
      </v-scroll-x-transition>
    </v-main>
  </v-app>
</template>


<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import TheSnackbar from "~/components/Layout/LayoutParts/TheSnackbar.vue";
import AppHeader from "@/components/Layout/LayoutParts/AppHeader.vue";
export default defineComponent({
  components: { TheSnackbar, AppHeader },
});
</script>
