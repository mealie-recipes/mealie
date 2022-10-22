import { Plugin } from "@nuxt/types";
import { Auth } from "@nuxtjs/auth-next";
import { Framework } from "vuetify";
import { icons } from "~/lib/icons";
import { Icon } from "~/lib/icons/icon-type";

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
    $auth: Auth;
  }
}

const globalsPlugin: Plugin = (_, inject) => {
  inject("globals", {
    icons,
  });
};

export default globalsPlugin;
