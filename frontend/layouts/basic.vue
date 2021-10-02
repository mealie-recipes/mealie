<template>
  <v-app dark>
    <TheSnackbar />
    <v-main>
      <v-scroll-x-transition>
        <Nuxt />
      </v-scroll-x-transition>
    </v-main>
    <AppFooter />
  </v-app>
</template>
  

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import AppFooter from "@/components/Layout/AppFooter.vue";
import TheSnackbar from "~/components/Layout/TheSnackbar.vue";

export default defineComponent({
  components: { AppFooter, TheSnackbar },
  setup() {
    return {};
  },
});
</script>
      
      <style scoped>
</style>+