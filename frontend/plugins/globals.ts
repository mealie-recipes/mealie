import { Plugin } from "@nuxt/types";
import { Framework } from "vuetify";
import { icons } from "~/utils/icons";
import { Icon } from "~/utils/icons/icon-type";

interface Globals {
  icons: Icon;
}

declare module "vue/types/vue" {
  interface Vue {
    $globals: Globals;
  }
}

declare module "@nuxt/types" {
  interface Context {
    $globals: Globals;
    $vuetify: Framework;
  }
}

const globalsPlugin: Plugin = (_, inject) => {
  inject("globals", {
    icons,
  });
};

export default globalsPlugin;
