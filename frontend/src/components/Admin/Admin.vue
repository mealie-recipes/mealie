<template>
  <v-container>
    <Theme />
    <Backup />
    <Webhooks />
    <Migration />
  </v-container>
</template>

<script>
import Backup from "./Backup";
import Webhooks from "./Webhooks";
import Theme from "./Theme";
import Migration from "./Migration";
export default {
  components: {
    Backup,
    Webhooks,
    Theme,
    Migration,
  },
};
</script>

<style>
</style>