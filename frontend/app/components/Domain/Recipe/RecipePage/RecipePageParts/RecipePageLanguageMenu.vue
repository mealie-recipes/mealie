<template>
  <div>
    <v-menu offset-y left>
      <template #activator="{ props: menuProps }">
        <v-badge
          :model-value="currentIsStale"
          color="warning"
          dot
          location="top end"
          offset-x="4"
          offset-y="4"
        >
          <v-tooltip location="bottom" color="info">
            <template #activator="{ props: tooltipProps }">
              <v-btn
                icon
                variant="flat"
                rounded="circle"
                size="small"
                color="info"
                v-bind="{ ...menuProps, ...tooltipProps }"
              >
                <v-icon size="x-large">
                  {{ $globals.icons.translate }}
                </v-icon>
              </v-btn>
            </template>
            <span>{{ currentLabel }}</span>
          </v-tooltip>
        </v-badge>
      </template>

      <v-list density="compact" min-width="240">
        <!-- Original -->
        <v-list-item
          :active="!selectedLocale"
          @click="select(null)"
        >
          <template #prepend>
            <v-icon>{{ !selectedLocale ? $globals.icons.check : $globals.icons.translate }}</v-icon>
          </template>
          <v-list-item-title>{{ $t("recipe.original-language") }}</v-list-item-title>
        </v-list-item>

        <!-- Stored translations -->
        <v-list-item
          v-for="t in translations"
          :key="t.locale"
          :active="selectedLocale === t.locale"
          @click="select(t.locale)"
        >
          <template #prepend>
            <v-icon>{{ selectedLocale === t.locale ? $globals.icons.check : $globals.icons.translate }}</v-icon>
          </template>
          <v-list-item-title>{{ localeName(t.locale) }}</v-list-item-title>
          <template #append>
            <v-icon
              v-if="t.isStale"
              color="warning"
              size="small"
              :title="$t('recipe.translation-outdated')"
            >
              {{ $globals.icons.alert }}
            </v-icon>
            <v-btn
              v-if="canEdit && t.isStale"
              icon
              variant="text"
              size="x-small"
              :loading="retranslating === t.locale"
              :disabled="loading"
              :title="$t('recipe.retranslate-recipe')"
              @click.stop="retranslate(t.locale)"
            >
              <v-icon>{{ $globals.icons.refresh }}</v-icon>
            </v-btn>
            <v-btn
              v-if="canEdit"
              icon
              variant="text"
              size="x-small"
              :title="$t('general.delete')"
              @click.stop="removeTranslation(t.locale)"
            >
              <v-icon>{{ $globals.icons.delete }}</v-icon>
            </v-btn>
          </template>
        </v-list-item>

        <!-- Translate action -->
        <template v-if="canEdit">
          <v-divider />
          <v-list-item
            :disabled="loading || !aiEnabled"
            @click="aiEnabled && (dialog = true)"
          >
            <template #prepend>
              <v-icon>{{ $globals.icons.translate }}</v-icon>
            </template>
            <v-list-item-title>{{ $t("recipe.translate-recipe") }}</v-list-item-title>
            <v-list-item-subtitle v-if="!aiEnabled">
              {{ $t("recipe.translate-requires-ai") }}
            </v-list-item-subtitle>
          </v-list-item>
        </template>
      </v-list>
    </v-menu>

    <BaseDialog
      v-model="dialog"
      :title="$t('recipe.translate-recipe')"
      :icon="$globals.icons.translate"
      can-submit
      :submit-disabled="!targetLocale"
      :submit-text="$t('recipe.translate-recipe')"
      :loading="loading"
      @submit="translate"
    >
      <v-card-text>
        <p class="mb-2">
          {{ $t("recipe.translate-recipe-description") }}
        </p>
        <v-autocomplete
          v-model="targetLocale"
          :items="localeOptions"
          item-title="name"
          item-value="value"
          :label="$t('language-dialog.choose-language')"
          variant="outlined"
          density="compact"
          hide-details
        />
      </v-card-text>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import { useGroupSelf } from "~/composables/use-groups";
import { useLocales } from "~/composables/use-locales";
import { alert } from "~/composables/use-toast";
import type { RecipeTranslationSummary } from "~/lib/api/types/recipe";

interface Props {
  slug: string;
  canEdit?: boolean;
  selectedLocale?: string | null;
}
const props = withDefaults(defineProps<Props>(), {
  canEdit: false,
  selectedLocale: null,
});

const emit = defineEmits<{
  (e: "switch", locale: string | null): void;
}>();

const api = useUserApi();
const i18n = useI18n();
const { group } = useGroupSelf();
const { locales } = useLocales();

const translations = ref<RecipeTranslationSummary[]>([]);
const dialog = ref(false);
const loading = ref(false);
const retranslating = ref<string | null>(null);
const targetLocale = ref<string | null>(null);

const aiEnabled = computed(() => !!group.value?.aiProviderSettings?.aiEnabled);

const localeOptions = computed(() => {
  const existing = new Set(translations.value.map(t => t.locale));
  return locales.filter(l => !existing.has(l.value));
});

function localeName(value: string): string {
  return locales.find(l => l.value === value)?.name ?? value;
}

const currentLabel = computed(() =>
  props.selectedLocale ? localeName(props.selectedLocale) : i18n.t("recipe.original-language"),
);

const currentIsStale = computed(() =>
  !!props.selectedLocale && !!translations.value.find(t => t.locale === props.selectedLocale)?.isStale,
);

async function loadTranslations() {
  const { data } = await api.recipes.getTranslations(props.slug);
  if (data) {
    translations.value = data;
  }
}

function select(locale: string | null) {
  emit("switch", locale);
}

async function translate() {
  if (!targetLocale.value) {
    return;
  }
  loading.value = true;
  const { data, error } = await api.recipes.translate(props.slug, targetLocale.value);
  if (error || !data) {
    loading.value = false;
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  const chosen = targetLocale.value;
  targetLocale.value = null;
  await loadTranslations();
  emit("switch", chosen);
  loading.value = false;
}

async function retranslate(locale: string) {
  retranslating.value = locale;
  const { data, error } = await api.recipes.translate(props.slug, locale);
  retranslating.value = null;
  if (error || !data) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  await loadTranslations();
  // If we're currently viewing this locale, re-fetch so the refreshed translation is shown.
  if (props.selectedLocale === locale) {
    emit("switch", locale);
  }
}

async function removeTranslation(locale: string) {
  const { error } = await api.recipes.deleteTranslation(props.slug, locale);
  if (error) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }
  if (props.selectedLocale === locale) {
    emit("switch", null);
  }
  await loadTranslations();
}

onMounted(loadTranslations);
</script>
