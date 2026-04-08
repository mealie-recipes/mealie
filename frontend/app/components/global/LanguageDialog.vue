<template>
  <BaseDialog
    v-model="modelValue"
    :icon="$globals.icons.translate"
    :title="$t('language-dialog.choose-language')"
  >
    <v-card-text>
      {{ $t("language-dialog.select-description") }}
      <v-autocomplete
        v-model="selectedLocale"
        :items="locales"
        :custom-filter="normalizeFilter"
        item-title="name"
        item-value="value"
        class="my-3"
        hide-details
        variant="outlined"
        @update:model-value="onLocaleSelect"
      >
        <template #item="{ item, props }">
          <div
            v-bind="props"
            class="px-2 py-2"
          >
            <v-list-item-title> {{ item.raw.name }} </v-list-item-title>
            <v-list-item-subtitle>
              {{ item.raw.progress }}% {{ $t("language-dialog.translated") }}
            </v-list-item-subtitle>
          </div>
        </template>
      </v-autocomplete>
      <i18n-t keypath="language-dialog.how-to-contribute-description">
        <template #read-the-docs-link>
          <a
            href="https://docs.mealie.io/contributors/translating/"
            target="_blank"
          >
            {{ $t("language-dialog.read-the-docs") }}
          </a>
        </template>
      </i18n-t>
    </v-card-text>
  </BaseDialog>
</template>

<script setup lang="ts">
import { useLocales } from "~/composables/use-locales";
import { normalizeFilter } from "~/composables/use-utils";

const modelValue = defineModel<boolean>({ default: () => false });

const { locales: LOCALES, locale, i18n } = useLocales();

const selectedLocale = ref(locale.value);
const onLocaleSelect = (value: string) => {
  if (value && locales.some(l => l.value === value)) {
    locale.value = value as any;
  }
};

watch(locale, () => {
  modelValue.value = false; // Close dialog when locale changes
});

const locales = LOCALES.filter(lc =>
  i18n.locales.value.map(i18nLocale => i18nLocale.code).includes(lc.value as any),
);
</script>
