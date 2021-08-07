<template>
  <v-container fluid>
    <BaseCardSectionTitle title="Event Notifications">
      {{ $t("events.new-notification-form-description") }}
    </BaseCardSectionTitle>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  layout: "admin",
  setup() {
    return {};
  },
});
</script>
    
<style scoped>
</style>