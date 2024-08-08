import * as locale from "vuetify/lib/locale";

// Ensure not null or undefined
if (!locale || !locale.en) {
  throw new Error("Vuetify locale not found");
}

export default {
  customVariables: ["~/assets/variables.scss"],
  icons: {
    iconfont: "mdiSvg", // 'mdi' || 'mdiSvg' || 'md' || 'fa' || 'fa4' || 'faSvg'
  },
  defaultAssets: false,
  theme: {
    options: {
      customProperties: true,
    },
    dark: false,
    // Theme Config set at runtime by /plugins/theme.ts
    // This config doesn't do anything.
    themes: {
      dark: {
        primary: "#E58325",
        accent: "#007A99",
        secondary: "#973542",
        success: "#43A047",
        info: "#1976d2",
        warning: "#FF6D00",
        error: "#EF5350",
      },
      light: {
        primary: "#E58325",
        accent: "#007A99",
        secondary: "#973542",
        success: "#43A047",
        info: "#1976d2",
        warning: "#FF6D00",
        error: "#EF5350",
      },
    },
  },
  lang: {
    locales: {
      "el-GR": locale.el,
      "it-IT": locale.it,
      "ko-KR": locale.ko,
      "es-ES": locale.es,
      "ja-JP": locale.ja,
      "bg-BG": locale.bg,
      "zh-CN": locale.zhHans,
      "tr-TR": locale.tr,
      "ar-SA": locale.ar,
      "hu-HU": locale.hu,
      "pt-PT": locale.pt,
      "no-NO": locale.no,
      "sv-SE": locale.sv,
      "ro-RO": locale.ro,
      "sk-SK": locale.sk,
      "uk-UA": locale.uk,
      "lt-LT": locale.lt,
      "fr-CA": locale.fr,
      "pl-PL": locale.pl,
      "da-DK": locale.da,
      "pt-BR": locale.pt,
      "de-DE": locale.de,
      "ca-ES": locale.ca,
      "sr-SP": locale.srCyrl,
      "cs-CZ": locale.cs,
      "fr-FR": locale.fr,
      "fr-BE": locale.fr,
      "zh-TW": locale.zhHant,
      "af-ZA": locale.af,
      "sl-SI": locale.sl,
      "ru-RU": locale.ru,
      "he-IL": locale.he,
      "nl-NL": locale.nl,
      "en-US": locale.en,
      "en-GB": locale.en,
      "fi-FI": locale.fi,
      "vi-VN": locale.vi,
    },
    current: "en-US",
  },
};
