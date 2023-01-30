import * as locale from "vuetify/lib/locale";

// Ensure not null or undefined
if (!locale || !locale.en) {
  throw new Error("Vuetify locale not found");
}

export default {
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
  theme: {},
};
