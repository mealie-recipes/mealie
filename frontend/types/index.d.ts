import { Auth } from "@nuxtjs/auth-next";

declare module "vue/types/vue" {
  interface Vue {
    $auth: Auth;
  }
}
