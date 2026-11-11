<template>
  <span v-html="value" />
</template>

<script setup lang="ts">
import { sanitizeInlineHtml } from "~/lib/sanitize";

// For short app-built strings with fraction or emphasis markup, such as yields and ingredient lines.
// Use <SafeMarkdown> for user-authored text.
const props = defineProps<{
  html?: string | null;
}>();

const value = computed(() => sanitizeInlineHtml(props.html));
</script>
