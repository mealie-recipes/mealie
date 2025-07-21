import type { LocaleObject } from "@nuxtjs/i18n";
import { LOCALES } from "./available-locales";

export const useLocales = () => {
  const i18n = useI18n();
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

  // auto update vuetify locale
  watch(locale, (lc) => {
    updateLocale(lc);
  });

  // set initial locale
  if (i18n.locale.value) {
    updateLocale(i18n.locale.value);
  };

  return {
    locale,
    locales: LOCALES,
    i18n,
  };
};
