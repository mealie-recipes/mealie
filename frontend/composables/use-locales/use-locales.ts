import { computed, useContext } from "@nuxtjs/composition-api";
import { LOCALES } from "./available-locales";

export const useLocales = () => {
  const { i18n, $vuetify } = useContext();

  function getLocale(value: string) {
    const currentLocale = LOCALES.filter((locale) => locale.value === value);
    return currentLocale.length ? currentLocale[0] : null;
  }

  const locale = computed<string>({
    get() {
      // dirty hack
      $vuetify.lang.current = i18n.locale;
      const currentLocale = getLocale(i18n.locale);
      if (currentLocale) {
        $vuetify.rtl = currentLocale.dir === "rtl";
      }

      return i18n.locale;
    },
    set(value) {
      i18n.setLocale(value);

      // this does not persist after window reload :-(
      $vuetify.lang.current = value;
      const currentLocale = getLocale(value);
      if (currentLocale) {
        $vuetify.rtl = currentLocale.dir === "rtl";
      }

      // Reload the page to update the language - not all strings are reactive
      window.location.reload();
    },
  });

  return {
    locale,
    locales: LOCALES,
    i18n,
  };
};
