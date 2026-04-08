<template>
  <BannerWarning
    :title="$t('banner-experimental.title')"
    :description="$t('banner-experimental.description')"
  >
    <template
      v-if="issue"
      #default
    >
      <a
        :href="issue"
        target="_blank"
      >{{ $t("banner-experimental.issue-link-text") }}</a>
    </template>
  </BannerWarning>
</template>

<script setup lang="ts">
defineProps({
  issue: {
    type: String,
    required: false,
    default: "",
  },
});
</script>
