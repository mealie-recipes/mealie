<template>
  <div v-html="value" />
</template>

<script setup lang="ts">
import type { PropType } from "vue";
import { renderMarkdown } from "~/lib/sanitize";

const props = defineProps({
  source: {
    type: String as PropType<string | null>,
    default: "",
  },
});

const { $appInfo } = useNuxtApp();

const value = computed(() => renderMarkdown(props.source, $appInfo?.allowedIframeHosts ?? []));
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

/* The app removes paragraph margins globally, which would show a blank line in the
   source as a plain line break. Space only between paragraphs, so a single paragraph
   keeps its layout. */
:deep(p + p) {
  margin-top: 0.5em;
}
</style>
