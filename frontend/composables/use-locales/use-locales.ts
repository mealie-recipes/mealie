import type { LocaleObject } from "@nuxtjs/i18n";
import { LOCALES } from "./available-locales";

export const useLocales = () => {
  const i18n = useI18n();
  const { current: vuetifyLocale, isRtl } = useLocale();

  const locale = computed<LocaleObject["code"]>({
    get: () => i18n.locale.value,
    set(value) {
      i18n.setLocale(value);
    },
  });
  // auto update vuetify locale
  watch(locale, (lc) => {
    vuetifyLocale.value = lc;
    const currentLocale = LOCALES.find(lc => lc.value === vuetifyLocale.value);
    if (currentLocale) {
      isRtl.value = currentLocale.dir === "rtl";
    }

    useHead({
      htmlAttrs: {
        lang: lc,
        dir: isRtl.value ? "rtl" : "ltr",
      },
    })
  });

  return {
    locale,
    locales: LOCALES,
    i18n,
  };
};
