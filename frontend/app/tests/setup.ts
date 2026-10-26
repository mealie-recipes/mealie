import { config } from "@vue/test-utils";
import { createI18n } from "vue-i18n";

function loadEnLocales() {
  /* eslint-disable @typescript-eslint/no-require-imports */
  return {
    ...require("../lang/messages/en-US.json"),
    // app/lang/locales/*.ts merge these in at runtime; do the same here so unit names resolve
    "unit-names": require("../../../mealie/repos/seed/resources/units/locales/en-US.json"),
  } as Record<string, string>;
  /* eslint-enable @typescript-eslint/no-require-imports */
}

const i18n = createI18n({
  locale: "en-US",
  messages: {
    "en-US": loadEnLocales(),
  },
});

config.global.plugins = [...(config.global.plugins ?? []), i18n];

export { i18n };
