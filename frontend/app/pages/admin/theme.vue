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

    <v-card-text class="pt-0">
      <div class="text-subtitle-1 mb-1">
        {{ $t("admin.theme.presets") }}
      </div>
      <div class="text-body-2 text-medium-emphasis mb-3">
        {{ $t("admin.theme.presets-description") }}
      </div>
      <div class="d-flex flex-wrap ga-3">
        <v-card
          v-for="preset in THEME_PRESETS"
          :key="preset.key"
          variant="outlined"
          class="preset-card pa-3"
          :class="{ 'preset-card--flat': preset.theme.cardStyle === 'flat' }"
          :style="{ borderRadius: previewRadiusPx(preset) }"
          :loading="applyingPreset === preset.key"
          @click="applyPreset(preset)"
        >
          <div class="d-flex ga-1 mb-2">
            <span
              v-for="color in previewColors(preset)"
              :key="color"
              class="preset-swatch"
              :style="{ backgroundColor: color }"
            />
          </div>
          <div class="text-body-2">
            {{ $t(preset.labelKey) }}
          </div>
        </v-card>
      </div>
    </v-card-text>

    <v-divider class="my-4" />

    <v-form
      v-if="form"
      @submit.prevent="save"
    >
      <v-card
        variant="outlined"
        class="pa-2 mb-4"
      >
        <v-card-title>{{ $t("admin.theme.design") }}</v-card-title>
        <v-card-text>
          <v-row>
            <v-col
              cols="12"
              md="6"
            >
              <v-select
                v-model="form.borderRadius"
                :label="$t('admin.theme.border-radius')"
                :items="borderRadiusOptions"
                variant="outlined"
                density="compact"
                hide-details
              />
            </v-col>
            <v-col
              cols="12"
              md="6"
            >
              <v-select
                v-model="form.cardStyle"
                :label="$t('admin.theme.card-style')"
                :items="cardStyleOptions"
                variant="outlined"
                density="compact"
                hide-details
              />
            </v-col>
            <v-col
              cols="12"
              md="6"
            >
              <v-select
                v-model="form.fontFamily"
                :label="$t('admin.theme.font-family')"
                :items="fontFamilyOptions"
                variant="outlined"
                density="compact"
                hide-details
              >
                <template #item="{ item, props: itemProps }">
                  <v-list-item
                    v-bind="itemProps"
                    :style="{ fontFamily: FONT_STACKS[item.value] }"
                  />
                </template>
              </v-select>
            </v-col>
            <v-col
              cols="12"
              md="6"
            >
              <v-select
                v-model="form.fontSize"
                :label="$t('admin.theme.font-size')"
                :items="fontSizeOptions"
                variant="outlined"
                density="compact"
                hide-details
              />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

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
import { useTheme } from "vuetify";
import { useAdminApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { THEME_PRESETS, type ThemePreset } from "~/composables/use-theme-presets";
import { applyDesignTokens, FONT_STACKS, RADIUS_PX } from "~/composables/use-theme-design";
import type { AppTheme } from "~/lib/api/types/non-generated";

definePageMeta({ layout: "admin" });

const { $globals } = useNuxtApp();
const i18n = useI18n();
const adminApi = useAdminApi();
const vuetifyTheme = useTheme();

const form = ref<AppTheme | null>(null);
const saving = ref(false);
const resetting = ref(false);
const applyingPreset = ref<string | null>(null);

function previewColors(preset: ThemePreset): string[] {
  const { theme } = preset;
  return [theme.lightPrimary, theme.lightAccent, theme.lightSecondary, theme.lightSuccess];
}

function previewRadiusPx(preset: ThemePreset): string {
  return RADIUS_PX[preset.theme.borderRadius] ?? RADIUS_PX.soft!;
}

// The theme colors are otherwise only read once, when Vuetify itself is created
// (see plugins/theme.ts) - saving new ones here wouldn't be visible in this same tab without
// this, even though they're already persisted and other tabs/users will pick them up on their
// next load.
function applyThemeLive(appTheme: AppTheme) {
  Object.assign(vuetifyTheme.themes.value.light.colors, {
    primary: appTheme.lightPrimary,
    accent: appTheme.lightAccent,
    secondary: appTheme.lightSecondary,
    success: appTheme.lightSuccess,
    info: appTheme.lightInfo,
    warning: appTheme.lightWarning,
    error: appTheme.lightError,
  });
  Object.assign(vuetifyTheme.themes.value.dark.colors, {
    primary: appTheme.darkPrimary,
    accent: appTheme.darkAccent,
    secondary: appTheme.darkSecondary,
    success: appTheme.darkSuccess,
    info: appTheme.darkInfo,
    warning: appTheme.darkWarning,
    error: appTheme.darkError,
  });
  applyDesignTokens(appTheme);
}

const borderRadiusOptions = [
  { title: i18n.t("admin.theme.border-radius-sharp"), value: "sharp" },
  { title: i18n.t("admin.theme.border-radius-soft"), value: "soft" },
  { title: i18n.t("admin.theme.border-radius-round"), value: "round" },
];

const cardStyleOptions = [
  { title: i18n.t("admin.theme.card-style-elevated"), value: "elevated" },
  { title: i18n.t("admin.theme.card-style-flat"), value: "flat" },
];

const fontFamilyOptions = [
  { title: i18n.t("admin.theme.font-family-sans"), value: "sans" },
  { title: i18n.t("admin.theme.font-family-rounded"), value: "rounded" },
  { title: i18n.t("admin.theme.font-family-serif"), value: "serif" },
  { title: i18n.t("admin.theme.font-family-mono"), value: "mono" },
];

const fontSizeOptions = [
  { title: i18n.t("admin.theme.font-size-small"), value: "small" },
  { title: i18n.t("admin.theme.font-size-medium"), value: "medium" },
  { title: i18n.t("admin.theme.font-size-large"), value: "large" },
];

async function applyPreset(preset: ThemePreset) {
  applyingPreset.value = preset.key;
  const { data } = await adminApi.theme.update(preset.theme);
  applyingPreset.value = null;
  if (data) {
    form.value = data;
    applyThemeLive(data);
    alert.success(i18n.t("admin.theme.preset-applied", { name: i18n.t(preset.labelKey) }));
  }
  else {
    alert.error(i18n.t("admin.theme.preset-apply-failed"));
  }
}

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
    applyThemeLive(data);
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
  if (form.value) {
    applyThemeLive(form.value);
  }
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

.preset-card {
  width: 140px;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.preset-card:hover {
  transform: translateY(-2px);
}

.preset-card--flat {
  box-shadow: none !important;
}

.preset-swatch {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: inline-block;
}
</style>
