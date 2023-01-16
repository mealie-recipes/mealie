declare module "*.vue" {
  import Vue from "vue";
  export default Vue;
}

declare module "~auth/runtime" {
  export { LocalScheme, SchemeCheck } from "@nuxtjs/auth-next"
}
