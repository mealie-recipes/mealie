<template>
  <v-alert border="left" colored-border type="warning" elevation="2" :icon="$globals.icons.alert">
    <b>Experimental Feature</b>
    <div>This page contains experimental or still-baking features. Please excuse the mess.</div>
    <div v-if="issue != ''" class="py-2">
      <a :href="issue" target="_blank"> Track our progress here</a>
    </div>
  </v-alert>
</template>


<script lang="ts">
export default {
  props: {
    issue: {
      type: String,
      required: false,
      default: "",
    },
  },
};
</script>