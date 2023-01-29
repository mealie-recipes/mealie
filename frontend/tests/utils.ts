import VueI18n from "vue-i18n";
import Vue from "vue";

Vue.use(VueI18n)

function loadEnLocales() {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  return require("../lang/messages/en-US.json") as Record<string, string>;
}

export function stubI18n() {
  const i18n = new VueI18n({
    locale: "en-US",
    messages: {
      "en-US": loadEnLocales(),
    },
  })
  return i18n
}
