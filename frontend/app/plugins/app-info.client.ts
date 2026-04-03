import axios from "axios";
import type { AppInfo } from "~/lib/api/types/admin";
import { LOCALES } from "~/composables/use-locales/available-locales";
import { useLocales } from "~/composables/use-locales";

export default defineNuxtPlugin({
  async setup() {
    const { data } = await axios.get<AppInfo>("/api/app/about");

    const { resolveLocale } = useLocales();
    const available = LOCALES.map(l => l.value);

    const targetLocale = resolveLocale(data.defaultLocale, available);

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
