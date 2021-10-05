<template>
  <div>This Week</div>
</template>
  
  <script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  setup() {
    return {};
  },
  head() {
    return {
      title: this.$t("meal-plan.dinner-this-week") as string,
    };
  },
});
</script>
  
  <style scoped>
</style>