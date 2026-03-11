import axios from "axios";
import type { AppInfo } from "~/lib/api/types/admin";
import { LOCALES } from "~/composables/use-locales/available-locales";

const LOCALE_COOKIE = "mealie_locale";

function detectBrowserLocale(): string | null {
  if (typeof navigator === "undefined") return null;
  const available = LOCALES.map(l => l.value);
  for (const lang of navigator.languages || [navigator.language]) {
    // Exact match (e.g. "nl-NL")
    if (available.includes(lang)) return lang;
    // Prefix match (e.g. "nl" → "nl-NL")
    const prefix = lang.split("-")[0];
    const match = available.find(a => a.startsWith(prefix + "-") || a === prefix);
    if (match) return match;
  }
  return null;
}

function resolveDefaultLocale(serverDefault: string | undefined): string | null {
  if (!serverDefault || serverDefault === "auto") {
    return detectBrowserLocale();
  }
  return serverDefault;
}

export default defineNuxtPlugin({
  async setup() {
    const { data } = await axios.get<AppInfo>("/api/app/about");

    const localeCookie = useCookie(LOCALE_COOKIE, { maxAge: 365 * 24 * 60 * 60 });
    const targetLocale = localeCookie.value
      || resolveDefaultLocale(data.defaultLocale)
      || "en-US";

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
