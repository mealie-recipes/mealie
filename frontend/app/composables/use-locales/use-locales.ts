import type { LocaleObject } from "@nuxtjs/i18n";
import { LOCALES } from "./available-locales";
import { useGlobalI18n } from "../use-global-i18n";

const LOCALE_COOKIE = "mealie_locale";

export const useLocales = () => {
  const i18n = useGlobalI18n();
  const { current: vuetifyLocale } = useLocale();

  const locale = computed<LocaleObject["code"]>({
    get: () => i18n.locale.value,
    set(value) {
      i18n.setLocale(value);
    },
  });

  function updateLocale(lc: LocaleObject["code"]) {
    vuetifyLocale.value = lc;
  }

  // resolve locale (cookie + browser + server default)
  function resolveLocale(
    serverDefault: string | undefined,
    availableLocales: string[],
  ): string {
    const localeCookie = useCookie<string | null>(LOCALE_COOKIE, {
      maxAge: 365 * 24 * 60 * 60,
    });

    // cookie wins
    if (localeCookie.value) return localeCookie.value;

    // auto detection
    if (!serverDefault || serverDefault === "auto") {
      if (typeof navigator !== "undefined") {
        for (const lang of navigator.languages || [navigator.language]) {
          // exact match
          if (availableLocales.includes(lang)) return lang;

          // prefix match
          const prefix = lang.split("-")[0];
          const match = availableLocales.find(
            a => a.startsWith(prefix + "-") || a === prefix,
          );

          if (match) return match;
        }
      }

      return "en-US";
    }

    // fallback to server default
    return serverDefault;
  }

  // auto update vuetify locale
  watch(locale, (lc) => {
    updateLocale(lc);
  });

  // set initial locale
  if (i18n.locale.value) {
    updateLocale(i18n.locale.value);
  }

  return {
    locale,
    locales: LOCALES,
    i18n,
    resolveLocale,
  };
};
