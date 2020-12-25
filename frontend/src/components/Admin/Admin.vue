<template>
  <v-container>
    <Theme />
    <Backup />
    <Webhooks />
  </v-container>
</template>

<script>
import Backup from "./Backup";
import Webhooks from "./Webhooks";
import Theme from "./Theme";
export default {
  components: {
    Backup,
    Webhooks,
    Theme,
  },
};
</script>

<style>
</style>