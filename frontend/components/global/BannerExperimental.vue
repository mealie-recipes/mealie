<template>
  <BannerWarning
    :title="$tc('banner-experimental.title')"
    :description="$tc('banner-experimental.description')"
  >
    <template v-if="issue" #default>
      <a :href="issue" target="_blank">{{ $t("banner-experimental.issue-link-text") }}</a>
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
