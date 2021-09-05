import Vue from "vue";
import "@nuxt/types";

declare module "vue/types/vue" {
  interface Vue {
    $globals: any;
  }
}

declare module "vue/types/options" {
  interface ComponentOptions<V extends Vue> {
    $globals?: any;
  }
  interface ComponentOptions<V extends UseContextReturn> {
    $globals?: any;
  }
}
