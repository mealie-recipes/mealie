import type { Composer } from "vue-i18n";

let i18n: Composer | null = null;

export function useGlobalI18n() {
  if (!i18n) {
    i18n = useI18n();
  }
  return i18n;
}
