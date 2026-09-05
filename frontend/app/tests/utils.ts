import { mount } from "@vue/test-utils";
import { createI18n } from "vue-i18n";

function loadEnLocales() {
  /* eslint-disable @typescript-eslint/no-require-imports */
  return {
    ...require("../lang/messages/en-US.json"),
    // app/lang/locales/*.ts merge these in at runtime; do the same here so unit names resolve
    "unit-names": require("../../../mealie/repos/seed/resources/units/locales/en-US.json"),
  } as Record<string, unknown>;
  /* eslint-enable @typescript-eslint/no-require-imports */
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

export const makeWrapper = <T>(setup: () => T) => {
  const Wrapper = {
    template: "<div />",
    setup,
  };
  const { vm } = mount(Wrapper);
  return vm as unknown as ReturnType<typeof Wrapper.setup>;
};
