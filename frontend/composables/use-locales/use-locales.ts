import type { LocaleObject } from "@nuxtjs/i18n";
import { LOCALES } from "./available-locales";

export const useLocales = () => {
  const i18n = useI18n();

  const { isRtl } = useRtl();
  const { current: vuetifyLocale } = useLocale();

  const locale = computed<LocaleObject["code"]>({
    get: () => i18n.locale.value,
    set(value) {
      i18n.setLocale(value);
    },
  });
  // auto update vuetify locale
  watch(locale, (lc) => {
    vuetifyLocale.value = lc;
  });
  // auto update rtl
  watch(vuetifyLocale, (vl) => {
    const currentLocale = LOCALES.find(lc => lc.value === vl);
    if (currentLocale) {
      isRtl.value = currentLocale.dir === "rtl";
    }
  });

  return {
    locale,
    locales: LOCALES,
    i18n,
  };
};
