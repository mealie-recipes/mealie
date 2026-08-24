<template>
  <!-- eslint-disable-next-line vue/no-v-html is safe here because all HTML is sanitized with DOMPurify in setup() -->
  <div v-html="value" />
</template>

<script setup lang="ts">
import { marked } from "marked";
import { sanitizeMarkdownHtml } from "~/lib/sanitize/markdown";

const props = defineProps({
  source: {
    type: String,
    default: "",
  },
});

const { $appInfo } = useNuxtApp();

const value = computed(() => {
  const rawHtml = marked.parse(props.source || "", { async: false, breaks: true });
  return sanitizeMarkdownHtml(rawHtml, $appInfo?.allowedIframeHosts ?? []);
});
</script>

<style scoped>
:deep(table) {
  border-collapse: collapse;
  width: 100%;
}

:deep(th),
:deep(td) {
  border: 1px solid;
  padding: 8px;
  text-align: left;
}

:deep(th) {
  font-weight: bold;
}

:deep(ul),
:deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}
</style>
