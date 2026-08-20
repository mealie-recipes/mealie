import type { LocaleObject } from "@nuxtjs/i18n";
import { LOCALES } from "./available-locales";
import { useGlobalI18n } from "../use-global-i18n";
import { useMealieAuth } from "../use-mealie-auth";
import { useUserApi } from "~/composables/api";

export const useLocales = () => {
  const i18n = useGlobalI18n();
  const { current: vuetifyLocale } = useLocale();
  const auth = useMealieAuth();
  const api = useUserApi();

  const locale = computed<LocaleObject["code"]>({
    get: () => i18n.locale.value,
    set(value) {
      i18n.setLocale(value);

      const user = auth.user.value;
      if (auth.loggedIn.value && user && value !== user.locale) {
        user.locale = value; // update immediately so we don't have to wait for the db
        api.users.updateOne(user.id, { ...user, locale: value }, { suppressAlert: true });
      }
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

  console.log({
    locale,
    locales: LOCALES,
    i18n,
  })

  return {
    locale,
    locales: LOCALES,
    i18n,
  };
};
