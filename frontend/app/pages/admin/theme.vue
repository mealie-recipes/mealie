<template>
  <v-container
    fluid
    class="narrow-container"
  >
    <BasePageTitle divider>
      <template #header>
        <v-icon size="48">
          {{ $globals.icons.theme }}
        </v-icon>
      </template>
      <template #title>
        {{ $t("admin.theme.theme") }}
      </template>
    </BasePageTitle>

    <v-card-text class="pt-0 text-body-2">
      {{ $t("admin.theme.description") }}
    </v-card-text>

    <v-form
      v-if="form"
      @submit.prevent="save"
    >
      <v-row>
        <v-col
          v-for="section in sections"
          :key="section.key"
          cols="12"
          md="6"
        >
          <v-card
            variant="outlined"
            class="pa-2"
          >
            <v-card-title>{{ section.title }}</v-card-title>
            <v-card-text>
              <div
                v-for="field in colorFields"
                :key="`${section.key}-${field.key}`"
                class="d-flex align-center mb-3"
              >
                <input
                  v-model="form[fieldKey(section.key, field.key)]"
                  type="color"
                  class="color-swatch mr-3"
                  :aria-label="field.label"
                >
                <v-text-field
                  v-model="form[fieldKey(section.key, field.key)]"
                  :label="field.label"
                  density="compact"
                  variant="outlined"
                  hide-details
                />
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <div class="d-flex mt-4 ga-2">
        <BaseButton
          type="submit"
          :loading="saving"
        >
          {{ $t("general.save") }}
        </BaseButton>
        <BaseButton
          color="secondary"
          :loading="resetting"
          @click="reset"
        >
          {{ $t("admin.theme.reset-to-defaults") }}
        </BaseButton>
      </div>
    </v-form>
  </v-container>
</template>

<script setup lang="ts">
import { useAdminApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import type { AppTheme } from "~/lib/api/types/non-generated";

definePageMeta({ layout: "admin" });

const { $globals } = useNuxtApp();
const i18n = useI18n();
const adminApi = useAdminApi();

const form = ref<AppTheme | null>(null);
const saving = ref(false);
const resetting = ref(false);

const sections = [
  { key: "light", title: i18n.t("admin.theme.light-mode") },
  { key: "dark", title: i18n.t("admin.theme.dark-mode") },
] as const;

const colorFields = [
  { key: "Primary", label: i18n.t("admin.theme.primary") },
  { key: "Accent", label: i18n.t("admin.theme.accent") },
  { key: "Secondary", label: i18n.t("admin.theme.secondary") },
  { key: "Success", label: i18n.t("admin.theme.success") },
  { key: "Info", label: i18n.t("admin.theme.info") },
  { key: "Warning", label: i18n.t("admin.theme.warning") },
  { key: "Error", label: i18n.t("admin.theme.error") },
] as const;

function fieldKey(sectionKey: string, colorKey: string) {
  return `${sectionKey}${colorKey}` as keyof AppTheme;
}

async function load() {
  const { data } = await adminApi.theme.get();
  if (data) {
    form.value = data;
  }
}

async function save() {
  if (!form.value) {
    return;
  }
  saving.value = true;
  const { data } = await adminApi.theme.update(form.value);
  saving.value = false;
  if (data) {
    form.value = data;
    alert.success(i18n.t("admin.theme.saved"));
  }
  else {
    alert.error(i18n.t("admin.theme.save-failed"));
  }
}

async function reset() {
  resetting.value = true;
  await adminApi.theme.reset();
  resetting.value = false;
  await load();
  alert.success(i18n.t("admin.theme.reset-done"));
}

onMounted(load);
</script>

<style scoped>
.color-swatch {
  width: 36px;
  height: 36px;
  padding: 0;
  border: none;
  border-radius: 4px;
  flex-shrink: 0;
}
</style>
