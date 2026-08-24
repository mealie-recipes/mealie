import { config } from "@vue/test-utils";
import { createI18n } from "vue-i18n";

function loadEnLocales() {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  return require("../lang/messages/en-US.json") as Record<string, string>;
}

const i18n = createI18n({
  locale: "en-US",
  messages: {
    "en-US": loadEnLocales(),
  },
});

config.global.plugins = [...(config.global.plugins ?? []), i18n];

export { i18n };
