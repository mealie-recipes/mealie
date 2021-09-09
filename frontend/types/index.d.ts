import Auth from "@nuxtjs/auth-next/dist/core/auth";

declare module "vue/types/vue" {
  interface Vue {
    $auth: Auth;
  }
}
