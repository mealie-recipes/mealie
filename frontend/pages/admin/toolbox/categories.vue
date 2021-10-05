<template>
  <v-container fluid>
    <BaseCardSectionTitle title="Manage Categories"> </BaseCardSectionTitle>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  layout: "admin",
  setup() {
    return {};
  },
  head() {
    return {
      title: this.$t("sidebar.categories") as string,
    };
  },
});
</script>
    
<style scoped>
</style>