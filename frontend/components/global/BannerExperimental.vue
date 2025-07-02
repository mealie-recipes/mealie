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
