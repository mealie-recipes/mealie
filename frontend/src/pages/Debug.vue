<template>
  <v-container>
    <LastRecipe />
    <LogFile class="mt-2" />
  </v-container>
</template>

<script>
import LastRecipe from "@/components/Debug/LastRecipe";
import LogFile from "@/components/Debug/LogFile";
export default {
  components: {
    LastRecipe,
    LogFile,
  },
};
</script>

<style></style>
