<template>
  <BaseDialog
    v-model="dialog"
    :icon="$globals.icons.translate"
    :title="$t('language-dialog.choose-language')"
  >
    <v-card-text>
      {{ $t("language-dialog.select-description") }}
      <v-autocomplete
        v-model="locale"
        :items="locales"
        item-title="name"
        class="my-3"
        hide-details
        variant="outlined"
        offset
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

<script lang="ts">
import { useLocales } from "~/composables/use-locales";

export default defineNuxtComponent({
  props: {
    modelValue: {
      type: Boolean,
      required: true,
    },
  },
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    const dialog = computed({
      get: () => props.modelValue,
      set: value => emit("update:modelValue", value),
    });

    const { locales: LOCALES, locale, i18n } = useLocales();
    watch(locale, () => {
      dialog.value = false; // Close dialog when locale changes
    });

    const locales = LOCALES.filter(lc =>
      i18n.locales.value.map(i18nLocale => i18nLocale.code).includes(lc.value as any),
    );

    return {
      dialog,
      i18n,
      locales,
      locale,
    };
  },
});
</script>
