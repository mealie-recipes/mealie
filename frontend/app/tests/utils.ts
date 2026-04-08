import { createI18n } from "vue-i18n";

function loadEnLocales() {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  return require("../lang/messages/en-US.json") as Record<string, string>;
}

export function stubI18n() {
  const i18n = createI18n({
    locale: "en-US",
    messages: {
      "en-US": loadEnLocales(),
    },
  });
  return i18n.global;
}
