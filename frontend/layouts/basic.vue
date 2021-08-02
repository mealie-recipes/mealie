<template>
  <v-app dark>
    <!-- <TheSnackbar /> -->

    <AppHeader :menu="false"> </AppHeader>
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
import AppHeader from "@/components/Layout/AppHeader.vue";

export default defineComponent({
  components: { AppHeader, AppFooter },
  setup() {
    return {};
  },
});
</script>
      
      <style scoped>
</style>+