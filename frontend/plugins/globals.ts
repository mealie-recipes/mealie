import { Plugin } from "@nuxt/types";
import { Auth as NuxtAuth } from "@nuxtjs/auth-next";
import { Framework } from "vuetify";
import { UserOut } from "~/lib/api/types/user";
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
  // @ts-ignore https://github.com/nuxt-community/auth-module/issues/1097#issuecomment-840249428
  interface Auth extends NuxtAuth {
    user: UserOut | null;
  }

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
