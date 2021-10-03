import Vue from "vue";
import "@nuxt/types";
import { Icon } from "~/utils/icons/icon-type";

interface Globals {
  icons: Icon;
}

declare module "vue/types/vue" {
  interface Vue {
    $globals: any;
  }
}

declare module "vue/types/options" {
  interface ComponentOptions<V extends Vue> {
    $globals?: Globals;
  }
  interface ComponentOptions<V extends UseContextReturn> {
    $globals?: Globals;
  }
}
