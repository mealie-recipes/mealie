<template>
  <span v-html="value" />
</template>

<script setup lang="ts">
import { sanitizeInlineHtml } from "~/lib/sanitize";

// For short inline text, user text included, such as yields and ingredient lines. Only fraction
// and emphasis tags survive and all attributes are removed. Use <SafeMarkdown> for markdown.
const props = defineProps<{
  html?: string | null;
}>();

const value = computed(() => sanitizeInlineHtml(props.html));
</script>
