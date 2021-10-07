<template>
  <v-container fluid>
    <BaseCardSectionTitle title="Organize Recipes"> </BaseCardSectionTitle>
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
      title: this.$t("settings.organize") as string,
    };
  },
});
</script>
    
<style scoped>
</style>