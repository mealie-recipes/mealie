<template>
  <div class="d-flex align-center">
    <span
      v-if="state === 'success'"
      class="text-caption font-weight-medium mr-2"
      :class="latencyColorClass"
    >
      {{ result?.latencyMs }}ms
    </span>
    <a
      v-else-if="state === 'warning' || state === 'failed'"
      href="#"
      class="text-caption font-weight-medium mr-2 text-decoration-underline"
      :class="state === 'warning' ? 'text-warning' : 'text-error'"
      @click.prevent="detailsOpen = true"
    >
      {{ $t('group.ai-provider-settings.view-details') }}
    </a>

    <BaseDialog
      v-model="detailsOpen"
      :title="state === 'warning'
        ? $t('group.ai-provider-settings.test-connection-model-not-found')
        : $t('group.ai-provider-settings.test-connection-failed')"
      :icon="$globals.icons.alert"
      :color="state === 'warning' ? 'warning' : 'error'"
    >
      <v-card-text>
        {{ result?.message }}
      </v-card-text>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { useAIProviders } from "~/composables/use-ai-providers";
import type { AIProviderTestResult } from "~/lib/api/types/group";

const props = defineProps<{
  providerId: string;
  autoTest: boolean;
}>();

const { $globals } = useNuxtApp();
const { testSavedOne } = useAIProviders();

type State = "idle" | "testing" | "success" | "warning" | "failed";

const state = ref<State>("idle");
const result = ref<AIProviderTestResult | null>(null);
const detailsOpen = ref(false);

const latencyColorClass = computed(() => {
  const ms = result.value?.latencyMs ?? 0;
  if (ms < 1000) return "text-success";
  if (ms < 1200) return "text-warning";
  return "text-error";
});

const emit = defineEmits<{
  (e: "testing-change", testing: boolean): void;
}>();

async function runTest() {
  state.value = "testing";
  emit("testing-change", true);
  try {
    const { data } = await testSavedOne(props.providerId);
    result.value = data;
    if (!data?.success) state.value = "failed";
    else if (data.modelFound === false) state.value = "warning";
    else state.value = "success";
  }
  finally {
    emit("testing-change", false);
  }
}

// Re-run whenever the parent's AutoTest switch turns on (including on initial mount, if it
// was already on when this row was created).
watch(
  () => props.autoTest,
  (autoTest) => {
    if (autoTest) runTest();
  },
  { immediate: true },
);

// The retry action itself lives in the parent's BaseButtonGroup, alongside edit/delete, so it
// matches their styling — the parent calls this directly via a template ref. `testing-change` lets
// the parent show a loading spinner on that button instead of duplicating one here, covering both
// a manual click and an auto-triggered run (the AutoTest switch calls runTest() internally above).
defineExpose({ runTest });
</script>
