import axios from "axios";
import type { AppInfo } from "~/lib/api/types/admin";

const LOCALE_COOKIE = "mealie_locale";

export default defineNuxtPlugin({
  async setup() {
    const { data } = await axios.get<AppInfo>("/api/app/about");

    const localeCookie = useCookie(LOCALE_COOKIE, { maxAge: 365 * 24 * 60 * 60 });
    const targetLocale = localeCookie.value || data.defaultLocale || "en-US";

    const { $i18n } = useNuxtApp();
    if ($i18n && targetLocale !== $i18n.locale.value) {
      await $i18n.setLocale(targetLocale);
    }

    return {
      provide: {
        appInfo: data,
      },
    };
  },
});
