<template>
<BaseDialog v-model="dialog" :icon="$globals.icons.translate" :title="$t('language-dialog.choose-language')">
  <v-card-text>
    {{ $t('language-dialog.select-description') }}
    <v-select
      v-model="locale"
      :items="locales"
      item-text="name"
      menu-props="auto"
      outlined
    ></v-select>
    <i18n path="language-dialog.how-to-contribute-description">
      <template #read-the-docs-link>
        <a href="https://docs.mealie.io/contributors/translating/" target="_blank">{{ $t("language-dialog.read-the-docs") }}</a>
      </template>
    </i18n>
  </v-card-text>
</BaseDialog>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import type { LocaleObject } from "@nuxtjs/i18n";

export default defineComponent({
  props: {
    value: {
      type: Boolean,
      default: false
    }
  },
  setup(props, context) {
    const dialog = computed<boolean>({
      get() {
        return props.value;
      },
      set(val) {
        context.emit("input", val);
      },
    });

    const { i18n } = useContext();

    const locales = [
      {
        name: "American English",
        value: "en-US",
      },
      {
        name: "British English",
        value: "en-GB",
      },
      {
        name: "Afrikaans (Afrikaans)",
        value: "af-ZA",
      },
      {
        name: "العربية (Arabic)",
        value: "ar-SA",
      },
      {
        name: "Català (Catalan)",
        value: "ca-ES",
      },
      {
        name: "Čeština (Czech)",
        value: "cs-CZ",
      },
      {
        name: "Dansk (Danish)",
        value: "da-DK",
      },
      {
        name: "Deutsch (German)",
        value: "de-DE",
      },
      {
        name: "Ελληνικά (Greek)",
        value: "el-GR",
      },
      {
        name: "Español (Spanish)",
        value: "es-ES",
      },
      {
        name: "Suomi (Finnish)",
        value: "fi-FI",
      },
      {
        name: "Français (French)",
        value: "fr-FR",
      },
      {
        name: "עברית (Hebrew)",
        value: "he-IL",
      },
      {
        name: "Magyar (Hungarian)",
        value: "hu-HU",
      },
      {
        name: "Italiano (Italian)",
        value: "it-IT",
      },
      {
        name: "日本語 (Japanese)",
        value: "ja-JP",
      },
      {
        name: "한국어 (Korean)",
        value: "ko-KR",
      },
      {
        name: "Norsk (Norwegian)",
        value: "no-NO",
      },
      {
        name: "Nederlands (Dutch)",
        value: "nl-NL",
      },
      {
        name: "Polski (Polish)",
        value: "pl-PL",
      },
      {
        name: "Português do Brasil (Brazilian Portugese)",
        value: "pt-BR",
      },
      {
        name: "Português (Portugese)",
        value: "pt-PT",
      },
      {
        name: "Română (Romanian)",
        value: "ro-RO",
      },
      {
        name: "Pусский (Russian)",
        value: "ru-RU",
      },
      {
        name: "српски (Serbian)",
        value: "sr-SP",
      },
      {
        name: "Svenska (Swedish)",
        value: "sv-SE",
      },
      {
        name: "Türkçe (Turkish)",
        value: "tr-TR",
      },
      {
        name: "Українська (Ukrainian)",
        value: "uk-UA",
      },
      {
        name: "Tiếng Việt (Vietnamese)",
        value: "vi-VN",
      },
      {
        name: "简体中文 (Chinese simplified)",
        value: "zh-CN",
      },
      {
        name: "繁體中文 (Chinese traditional)",
        value: "zh-TW",
      },
    ].filter(locale => (i18n.locales as LocaleObject[]).map(i18nLocale => i18nLocale.code).includes(locale.value));

    const locale = computed<string>({
      get() {
        return i18n.locale;
      },
      set(value) {
        i18n.setLocale(value);
        // Reload the page to update the language - not all strings are reactive
        window.location.reload();
      }
    });

    return {
      dialog,
      i18n,
      locales,
      locale,
    };
  }
});
</script>

<style scoped>

</style>
