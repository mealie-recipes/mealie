import { computed, useContext } from "@nuxtjs/composition-api";
import { LOCALES } from "./available-locales";

export const useLocales = () => {
  const { i18n } = useContext();

  const locale = computed<string>({
    get() {
      return i18n.locale;
    },
    set(value) {
      i18n.setLocale(value);
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
