<template>
  <div>
    <v-menu offset-y left>
      <template #activator="{ props: menuProps }">
        <v-btn
          variant="text"
          size="small"
          v-bind="menuProps"
        >
          <v-icon start>
            {{ $globals.icons.translate }}
          </v-icon>
          {{ currentLabel }}
          <v-icon
            v-if="currentIsStale"
            end
            color="warning"
            :title="$t('recipe.translation-outdated')"
          >
            {{ $globals.icons.alert }}
          </v-icon>
        </v-btn>
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
        <template v-if="canEdit && aiEnabled">
          <v-divider />
          <v-list-item :disabled="loading" @click="dialog = true">
            <template #prepend>
              <v-icon>{{ $globals.icons.translate }}</v-icon>
            </template>
            <v-list-item-title>{{ $t("recipe.translate-recipe") }}</v-list-item-title>
          </v-list-item>
        </template>
      </v-list>
    </v-menu>

    <BaseDialog
      v-model="dialog"
      :title="$t('recipe.translate-recipe')"
      :icon="$globals.icons.translate"
      can-confirm
      :submit-disabled="!targetLocale"
      :loading="loading"
      @confirm="translate"
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
  loading.value = false;
  if (error || !data) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  dialog.value = false;
  const chosen = targetLocale.value;
  targetLocale.value = null;
  await loadTranslations();
  emit("switch", chosen);
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
