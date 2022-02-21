<template>
  <v-app dark>
    <TheSnackbar />

    <v-main>
      <v-scroll-x-transition>
        <Nuxt />
      </v-scroll-x-transition>
    </v-main>
  </v-app>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import TheSnackbar from "~/components/Layout/TheSnackbar.vue";
export default defineComponent({
  components: { TheSnackbar },
});
</script>
