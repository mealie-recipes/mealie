<template>
  <v-alert border="left" colored-border type="warning" elevation="2" :icon="$globals.icons.alert">
    <b>{{ $t("banner-experimental.title") }}</b>
    <div>{{ $t("banner-experimental.description") }}</div>
    <div v-if="issue != ''" class="py-2">
      <a :href="issue" target="_blank">{{ $t("banner-experimental.issue-link-text") }}</a>
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
