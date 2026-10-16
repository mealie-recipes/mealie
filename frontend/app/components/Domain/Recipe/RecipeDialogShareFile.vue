<template>
  <BaseDialog v-model="dialog" bottom-sheet :title="$t('recipe-share.share-recipe-file')">
    <v-card-text>
      <p class="mb-4">
        {{ $t("recipe-share.recipe-file-description") }}
      </p>
      <v-progress-linear v-if="loading" indeterminate :aria-label="$t('general.loading')" />
      <v-alert v-if="failed" type="error" class="mb-4">
        {{ $t("events.something-went-wrong") }}
      </v-alert>
      <v-alert v-if="shareUnavailable" type="warning" class="mb-4">
        {{ $t("recipe-share.file-sharing-unavailable") }}
      </v-alert>
      <v-btn :disabled="!file || busy" color="primary" class="mr-2" @click="shareFile">
        {{ $t("recipe-share.share-recipe-file") }}
      </v-btn>
      <v-btn :disabled="!file || busy" variant="text" @click="downloadFile">
        {{ $t("general.download") }} JSON
      </v-btn>
    </v-card-text>
  </BaseDialog>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import { createRecipeFile, downloadRecipeFile, shareRecipeFile } from "~/lib/recipe/recipe-file";

const props = defineProps<{ slug: string }>();
const dialog = defineModel<boolean>({ default: false });
const api = useUserApi();
const file = shallowRef<File>();
const loading = ref(false);
const busy = ref(false);
const failed = ref(false);
const shareUnavailable = ref(false);

// Fetch through the existing authenticated export endpoint, not the page's
// recipe prop or public/share-token endpoints. A second click retains Web Share's
// transient user activation even when preparing the file takes a long time.
watch([dialog, () => props.slug], async ([open, slug], _, onCleanup) => {
  let active = true;
  onCleanup(() => { active = false; });
  file.value = undefined;
  failed.value = false;
  shareUnavailable.value = false;
  loading.value = false;
  if (!open) return;
  loading.value = true;
  try {
    const { data, error } = await api.recipes.exportRaw(slug);
    if (!active) return;
    if (error || !data) throw new Error("Export failed");
    file.value = createRecipeFile(data, slug);
  }
  catch {
    if (active) failed.value = true;
  }
  finally {
    if (active) loading.value = false;
  }
}, { immediate: true });

async function shareFile() {
  if (!file.value || busy.value) return;
  busy.value = true;
  shareUnavailable.value = false;
  try {
    shareUnavailable.value = await shareRecipeFile(file.value) === "unavailable";
  }
  catch {
    failed.value = true;
  }
  finally {
    busy.value = false;
  }
}

function downloadFile() {
  if (file.value && !busy.value) downloadRecipeFile(file.value);
}
</script>
