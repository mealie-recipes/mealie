import { computed, useContext } from "@nuxtjs/composition-api";
import { LOCALES } from "./available-locales";

export const useLocales = () => {
  const { i18n, $vuetify } = useContext();

  const locale = computed<string>({
    get() {
      $vuetify.lang.current = i18n.locale; // dirty hack
      return i18n.locale;
    },
    set(value) {
      i18n.setLocale(value);
      $vuetify.lang.current = value; // this does not persist after window reload :-(

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
