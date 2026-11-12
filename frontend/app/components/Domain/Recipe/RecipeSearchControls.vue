<template>
  <div v-if="query?.trim()" class="my-2">
    <div class="d-flex align-center flex-wrap ga-2">
      <v-btn
        size="small"
        color="primary"
        variant="tonal"
        rounded="lg"
        :prepend-icon="mode === 'all' ? mdiArrowExpandHorizontal : mdiArrowCollapseHorizontal"
        :aria-pressed="mode === 'any'"
        @click="emit('update:mode', mode === 'all' ? 'any' : 'all')"
      >
        {{ $t(mode === "all" ? "search.broaden-search" : "search.show-strong-matches") }}
      </v-btn>
    </div>
    <p v-if="mode === 'any'" role="status" class="text-caption text-medium-emphasis mt-2 mb-0">
      {{ $t("search.partial-matches") }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { mdiArrowCollapseHorizontal, mdiArrowExpandHorizontal } from "@mdi/js";

defineProps<{ query: string | null; mode: "all" | "any" }>();
const emit = defineEmits<{ "update:mode": [mode: "all" | "any"] }>();
</script>
